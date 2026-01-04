package com.api.clowner.generator;

import org.telegram.telegrambots.meta.api.methods.updates.GetUpdates;
import java.util.List;
import java.util.function.Function;

public class CustomGetUpdatesGenerator implements Function<Integer, GetUpdates> {
    private static final int GET_UPDATES_LIMIT = 100;
    private static final int GET_UPDATES_TIMEOUT = 50;

    private final List<String> allowedUpdates;

    public CustomGetUpdatesGenerator() {

        this.allowedUpdates = List.of("message", "message_reaction");
    }

    public CustomGetUpdatesGenerator(List<String> allowedUpdates) {
        this.allowedUpdates = allowedUpdates;
    }

    @Override
    public GetUpdates apply(Integer lastReceivedUpdate) {
        return GetUpdates
                .builder()
                .limit(GET_UPDATES_LIMIT)
                .timeout(GET_UPDATES_TIMEOUT)
                .offset(lastReceivedUpdate + 1)
                .allowedUpdates(allowedUpdates) 
                .build();
    }
}