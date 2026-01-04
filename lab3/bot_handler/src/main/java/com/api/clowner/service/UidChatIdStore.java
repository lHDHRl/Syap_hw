package com.api.clowner.service;

import com.api.clowner.dto.CommonUid;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class UidChatIdStore {

    private final Map<CommonUid, Long> uidToChatIdMap = new ConcurrentHashMap<>();

    public void storeUidChatId(CommonUid uid, Long chatId) {
        uidToChatIdMap.put(uid, chatId);
    }

    public Long removeAndGetChatId(CommonUid uid) {
        return uidToChatIdMap.remove(uid);
    }
}