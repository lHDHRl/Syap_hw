package com.api.clowner.dto;

import com.fasterxml.jackson.annotation.JsonProperty;


public class CommonUid {

    @JsonProperty("SEQ")
    private int seq;

    @JsonProperty("NUM")
    private int num;

    public CommonUid() {}

    public CommonUid(int seq, int num) {
        this.seq = seq;
        this.num = num;
    }

    public int getSeq() { return seq; }
    public void setSeq(int seq) { this.seq = seq; }

    public int getNum() { return num; }
    public void setNum(int num) { this.num = num; }

    @Override
    public String toString() {
        return "Uid{SEQ=" + seq + ", NUM=" + num + '}';
    }


    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        CommonUid uid = (CommonUid) o;
        return seq == uid.seq && num == uid.num;
    }

    @Override
    public int hashCode() {
        return java.util.Objects.hash(seq, num);
    }
}