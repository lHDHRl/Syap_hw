package com.api.clowner.config;

import com.api.clowner.generator.CustomGetUpdatesGenerator;
import com.api.clowner.service.TelegramBotService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient;
import org.telegram.telegrambots.longpolling.TelegramBotsLongPollingApplication;
import org.telegram.telegrambots.meta.TelegramUrl;
import org.telegram.telegrambots.meta.generics.TelegramClient;

@Configuration
@Slf4j
public class TelegramBotConfig {

    @Value("${telegram.bot.token:}")
    private String botToken;

    @Bean
    public TelegramClient telegramClient() {

        return new OkHttpTelegramClient(botToken);
    }

    @Bean
    public CustomGetUpdatesGenerator customGetUpdatesGenerator() {

        return new CustomGetUpdatesGenerator();
    }

    @Bean
    public TelegramBotsLongPollingApplication telegramBotsLongPollingApplication(
            TelegramClient telegramClient,
            CustomGetUpdatesGenerator customGetUpdatesGenerator,
            TelegramBotService telegramBotService 
    ) {

        TelegramBotsLongPollingApplication application = new TelegramBotsLongPollingApplication();

        try {
            application.registerBot(
                botToken,
                () -> TelegramUrl.DEFAULT_URL,
                customGetUpdatesGenerator,
                telegramBotService 
            );

        } catch (Exception e) {
            log.error("Ошибка при регистрации бота в конфигурации: {}", e.getMessage(), e);
            throw new RuntimeException("Не удалось настроить Telegram бота", e);
        }


        return application;
    }

}