package com.api.clowner.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class InputMessage {

    @JsonProperty("useWhitelist")
    private boolean useWhitelist = true;

    @JsonProperty("uid")
    private CommonUid uid;

    @JsonProperty("imgData")
    private String imgData;

    public InputMessage() {}

    public InputMessage(boolean useWhitelist, CommonUid uid, String imgData) {
        this.useWhitelist = useWhitelist;
        this.uid = uid;
        this.imgData = imgData;
    }


    public boolean isUseWhitelist() { return useWhitelist; }
    public void setUseWhitelist(boolean useWhitelist) { this.useWhitelist = useWhitelist; }

    public CommonUid getUid() { return uid; }
    public void setUid(CommonUid uid) { this.uid = uid; }

    public String getImgData() { return imgData; }
    public void setImgData(String imgData) { this.imgData = imgData; }

    @Override
    public String toString() {
        return "ClownImageInputMessage{" +
                "useWhitelist=" + useWhitelist +
                ", uid=" + uid +
                ", imgData (length)=" + (imgData != null ? imgData.length() : 0) +
                '}';
    }

}