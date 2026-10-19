package io.github.mona1207.study;

import java.net.URI;

public final class UpdatePolicy {
    public static final String HOME = "https://mona1207.github.io/discrete-math/";
    public static final String MANIFEST = HOME + "version.json";
    public static final String DOWNLOAD = HOME + "download/";
    private UpdatePolicy() {}
    public static boolean trustedPage(String value) {
        try {
            URI u = new URI(value);
            return "https".equalsIgnoreCase(u.getScheme()) && "mona1207.github.io".equalsIgnoreCase(u.getHost())
                && (u.getPort() == -1 || u.getPort() == 443) && u.getRawUserInfo() == null
                && u.getPath().startsWith("/discrete-math/");
        } catch (Exception ignored) { return false; }
    }
    public static boolean newVersion(long installed, long offered) { return offered > installed && offered <= Integer.MAX_VALUE; }
    public static String safeDownload(String url) {
        return trustedPage(url) && url.startsWith(DOWNLOAD) && url.endsWith(".apk") ? url : DOWNLOAD;
    }
    public static String exportName(String name) {
        String safe = name == null ? "学习备份.json" : name.replaceAll("[\\\\/:*?\"<>|\\p{Cntrl}]", "_");
        return safe.isEmpty() ? "学习备份.json" : safe.substring(0, Math.min(120, safe.length()));
    }
}
