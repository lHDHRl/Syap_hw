package com.api.clowner.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class OutputMessage {

    @JsonProperty("uid")
    private CommonUid uid;

    @JsonProperty("imgData")
    private String imgData;


    @JsonProperty("foundFaceCount")
    private Integer foundFaceCount;

    @JsonProperty("clownedFaceCount")
    private Integer clownedFaceCount;

    @JsonProperty("status")
    private String status;

    public Integer getFoundFaceCount() {
        return foundFaceCount;
    }

    public void setFoundFaceCount(Integer foundFaceCount) {
        this.foundFaceCount = foundFaceCount;
    }

    public Integer getClownedFaceCount() {
        return clownedFaceCount;
    }

    public void setClownedFaceCount(Integer clownedFaceCount) {
        this.clownedFaceCount = clownedFaceCount;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }


    public CommonUid getUid() {
        return uid;
    }

    public void setUid(CommonUid uid) {
        this.uid = uid;
    }

    public String getImgData() {
        return imgData;
    }

    public void setImgData(String imgData) {
        this.imgData = imgData;
    }

    @Override
    public String toString() {
        return "OutputMessage{" +
                "uid=" + uid +
                ", imgData=... (base64 string) ... " +
                ", foundFaceCount=" + foundFaceCount +
                ", clownedFaceCount=" + clownedFaceCount +
                ", status='" + status + '\'' +
                '}';
    }
}