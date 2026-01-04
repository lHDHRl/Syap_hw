// Тут написано то, что подлежит рефактору, мне было лень прописывать в классном языке Java отдельно хендлеры,
//  потому что тогда бы жопа горела сильнее, так что наслаждаемся поистине потрясающими 300 строками в главном сервисе.








package com.api.clowner.service;
import com.api.clowner.dto.InputMessage;
import com.api.clowner.dto.CommonUid;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient;
import org.telegram.telegrambots.longpolling.interfaces.LongPollingUpdateConsumer;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.api.objects.message.Message;
import org.telegram.telegrambots.meta.api.objects.reactions.MessageReactionUpdated;
import org.telegram.telegrambots.meta.api.objects.reactions.ReactionTypeEmoji;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.meta.generics.TelegramClient;
import org.telegram.telegrambots.meta.api.methods.GetFile;
import org.telegram.telegrambots.meta.api.objects.photo.PhotoSize;
import jakarta.annotation.PostConstruct;
import java.io.InputStream;
import java.net.URL;
import java.util.List;
import java.util.Set;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Base64;
import java.util.Arrays;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class TelegramBotService implements LongPollingUpdateConsumer {

    private final TelegramClient telegramClient;
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final OkHttpTelegramClient okHttpTelegramClient;
    private final UidChatIdStore uidChatIdStore;

    private final Map<String, MessageInfo> messageInfoMap = new ConcurrentHashMap<>();
    private static class MessageInfo {
        final Long chatId;
        final List<PhotoSize> photoSizes;
        MessageInfo(Long chatId, List<PhotoSize> photoSizes) {
            this.chatId = chatId;
            this.photoSizes = photoSizes;
        }
    }

    @Value("${telegram.bot.token}")
    private String botToken;

    @Value("${kafka.topic.clown-image-input:clownImageInput}")
    private String clownImageInputTopic;

    @Value("${allowed.user.ids:}")
    private String allowedUserIdsString;

    private final Set<Long> whitelistUserIds = ConcurrentHashMap.newKeySet();

    private int globalSequenceCounter = 0;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @PostConstruct
    public void init() {
        if (allowedUserIdsString != null && !allowedUserIdsString.trim().isEmpty()) {
            whitelistUserIds.addAll(
                Arrays.stream(allowedUserIdsString.split(","))
                      .map(String::trim)
                      .mapToLong(Long::parseLong)
                      .boxed()
                      .collect(Collectors.toList())
            );
        }
    }

    @SneakyThrows
    @Override
    public void consume(List<Update> updates) {
        if (updates == null || updates.isEmpty()) {
            return;
        }

        for (Update update : updates) {
            if (update.hasMessage()) {
                Message message = update.getMessage();
                if ("private".equals(message.getChat().getType())) {
                    continue;
                }

                if (message.hasText()) {
                    String text = message.getText();
                    if ("/clown".equals(text)) {
                        processClownCommand(message);
                    }
                } else if (message.hasPhoto()) {
                    processNewMessage(message);
                }
            }

            if (update.getMessageReaction() != null) {
                processReaction(update.getMessageReaction());
            }
        }
    }

    private void processClownCommand(Message commandMessage) {
        Long userId = commandMessage.getFrom().getId();

        if (!whitelistUserIds.contains(userId)) {
            sendReplyMessage(commandMessage.getChatId(), commandMessage.getMessageId(), "Команда недоступна.");
            return;
        }

        if (commandMessage.getReplyToMessage() == null) {
             sendReplyMessage(commandMessage.getChatId(), commandMessage.getMessageId(), "Пожалуйста, ответьте на сообщение с фото командой /clown.");
             return;
        }

        Message repliedToMessage = commandMessage.getReplyToMessage();
        Integer repliedToMessageId = repliedToMessage.getMessageId();
        Long chatId = commandMessage.getChatId();

        String key = chatId + "_" + repliedToMessageId;
        MessageInfo storedInfo = messageInfoMap.get(key);

        if (storedInfo != null) {
            processImageAndSendToKafka(storedInfo.photoSizes, repliedToMessageId, false, commandMessage.getChatId(), commandMessage.getMessageId());
            messageInfoMap.remove(key);
        } else if (repliedToMessage.hasPhoto()) {
             processImageAndSendToKafka(repliedToMessage.getPhoto(), repliedToMessageId, false, commandMessage.getChatId(), commandMessage.getMessageId());
        } else {
             sendReplyMessage(commandMessage.getChatId(), commandMessage.getMessageId(), "Сообщение, на которое вы ответили, не содержит фото.");
        }
    }

    private void processNewMessage(Message message) {
        if (message.hasPhoto()) {
            var photoSizes = message.getPhoto();
            if (photoSizes != null && !photoSizes.isEmpty()) {
                Integer messageId = message.getMessageId();
                Long chatId = message.getChatId();
                String key = chatId + "_" + messageId;
                messageInfoMap.put(key, new MessageInfo(chatId, photoSizes));
            }
        }
    }

    private void processReaction(MessageReactionUpdated reaction) {
        boolean hasClownReaction = reaction.getNewReaction().stream()
                .filter(rt -> "emoji".equals(rt.getType()))
                .map(rt -> (ReactionTypeEmoji) rt)
                .anyMatch(rt -> "🤡".equals(rt.getEmoji()));

        if (!hasClownReaction) {
            return;
        }

        Long userId = reaction.getUser().getId();
        if (!whitelistUserIds.contains(userId)) {
            return;
        }

        Integer messageId = reaction.getMessageId();
        if (messageId == null) {
            return;
        }

        String key = reaction.getChat().getId() + "_" + messageId;
        MessageInfo storedInfo = messageInfoMap.get(key);

        if (storedInfo != null) {
            processImageAndSendToKafka(storedInfo.photoSizes, messageId, true, storedInfo.chatId, null);
            messageInfoMap.remove(key);
        }
    }

    private void processImageAndSendToKafka(List<PhotoSize> photoSizes, Integer messageId, boolean whitelist, Long chatId, Integer replyToMessageId) {
         var photoSize = photoSizes.get(photoSizes.size() - 1);
         String fileId = photoSize.getFileId();

         byte[] imageData = downloadFileBytes(fileId);
         if (imageData != null) {
             String base64ImageData = Base64.getEncoder().encodeToString(imageData);

            CommonUid uid = new CommonUid(globalSequenceCounter++, messageId.hashCode());

             InputMessage kafkaMessage = new InputMessage(
                     whitelist,
                     uid,
                     base64ImageData
             );

             try {
                 uidChatIdStore.storeUidChatId(uid, chatId);
                 kafkaTemplate.send(clownImageInputTopic, kafkaMessage);
             } catch (Exception e) {
                 uidChatIdStore.removeAndGetChatId(uid);
                 if (replyToMessageId != null) {
                     sendReplyMessage(chatId, replyToMessageId, "Ошибка при отправке фото.");
                 }
             }
         } else {
             if (replyToMessageId != null) {
                 sendReplyMessage(chatId, replyToMessageId, "Не удалось загрузить фото для обработки.");
             }
         }
    }

    @SneakyThrows
    private void sendReplyMessage(Long chatId, Integer replyToMessageId, String text) {
        SendMessage message = SendMessage.builder()
                .chatId(chatId)
                .text(text)
                .replyToMessageId(replyToMessageId)
                .build();

        try {
            telegramClient.execute(message);
        } catch (TelegramApiException e) {
        }
    }

    @SneakyThrows
    private byte[] downloadFileBytes(String fileId) {
        try {
            GetFile getFileRequest = GetFile.builder().fileId(fileId).build();
            org.telegram.telegrambots.meta.api.objects.File file = telegramClient.execute(getFileRequest);
            String filePath = file.getFilePath();

            String fileUrl = "https://api.telegram.org/file/bot" + botToken + "/" + filePath;

            URL url = new URL(fileUrl);
            try (InputStream inputStream = url.openStream()) {
                return inputStream.readAllBytes();
            }
        } catch (Exception e) {
            return null;
        }
    }
}