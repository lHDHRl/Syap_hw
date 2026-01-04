package com.api.clowner.service;

import com.api.clowner.dto.OutputMessage;
import com.api.clowner.dto.CommonUid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.methods.send.SendPhoto;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import org.telegram.telegrambots.meta.generics.TelegramClient;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.Base64;

@Service
@RequiredArgsConstructor
@Slf4j
public class KafkaConsumerService {

    private final TelegramClient telegramClient;
    private final UidChatIdStore uidChatIdStore;

    @Value("${kafka.topic.clown-image-output:clownImageOutput}")
    private String clownImageOutputTopic;

    @KafkaListener(
        topics = "#{@environment.getProperty('kafka.topic.clown-image-output', 'clownImageOutput')}",
        groupId = "clown-transformer",
        containerFactory = "outputMessageKafkaListenerContainerFactory"
    )
    public void consumeClownedImage(OutputMessage outputMessage) {
        try {
            String base64Image = outputMessage.getImgData();
            String status = outputMessage.getStatus();

            if (status == null || !status.equals("OK")) {

                CommonUid uid = outputMessage.getUid();
                if (uid == null) {
                    return; 
                }
                Long chatId = uidChatIdStore.removeAndGetChatId(uid);
                if (chatId != null) {
                    SendMessage msg = SendMessage.builder()
                            .chatId(chatId.toString())
                            .text("Плохое качество фото!")
                            .build();
                    telegramClient.execute(msg);
                }
                return; 
            }


            if (base64Image == null || base64Image.isEmpty()) {
                return;
            }

            byte[] imageBytes = Base64.getDecoder().decode(base64Image.trim());
            if (imageBytes.length == 0) {
                return;
            }

            CommonUid uid = outputMessage.getUid();
            if (uid == null) {
                return;
            }

            Long chatId = uidChatIdStore.removeAndGetChatId(uid);
            if (chatId == null) {
                return;
            }

            InputStream imageInputStream = new ByteArrayInputStream(imageBytes);
            SendPhoto sendPhoto = SendPhoto.builder()
                    .photo(new org.telegram.telegrambots.meta.api.objects.InputFile(imageInputStream, "clown_result.jpg"))
                    .chatId(chatId.toString())
                    .caption("Добро пожаловать в ИМКТ,\nКлоунизировано!")
                    .build();

            telegramClient.execute(sendPhoto);

        } catch (IllegalArgumentException e) {
        } catch (TelegramApiException e) {
        } catch (Exception e) {
        }
    }
}