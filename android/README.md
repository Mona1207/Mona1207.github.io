# 莫那刷题站 Android

Android 8.0+，包名 `io.github.mona1207.study`，当前版 `1.1.0 (2)`。应用通过同一 HTTPS 源加载最新版网站，保留独立 WebView 的 IndexedDB/本机笔记。浏览器与 App 数据各自独立，首次使用请通过网页备份导出、App 导入迁移。

- 启动、回到前台时自动检查 `discrete-math/version.json`，前台每 2 分钟检查一次；设置内可手动检查。发现更高的 `android.version_code` 后通过网页版本中心提醒，旧网页保留原生弹窗兜底；打开下载地址后由 Android 系统确认覆盖安装。
- 版本中心显示网页与 App 版本、更新内容，可关闭应用内提醒或选择 24 小时后提醒。应用关闭后不发系统通知。
- 网页更新脚本检查 `web_version`；更新前等待草稿保存，记录不清空。
- 支持系统文件选择、图片/JSON 备份导入；blob/data 图片与备份导出走系统“另存为”，单个导出上限 48MB。较大备份可在浏览器导出。
- 返回键先关闭选择菜单/选题目录，再走网页同层历史；主页面保存草稿后退出。主源以外链接交给系统浏览器。
- 无广告、无需账户，首次加载需要联网；未实现完整教材离线下载。

## 构建与后续更新

需要 JDK 17、Android SDK platform 35 与 build-tools 35.0.0，无第三方 Android 运行时依赖。只有 JRE 时可通过 `MONA_ECJ_JAR` 指向 Eclipse ECJ 3.37.0 编译器。

设置 `ANDROID_HOME`、`MONA_KEYSTORE`、`MONA_STORE_PASSWORD` 后执行 `python3 android/build.py`。首次发行的私有签名备份须保留；后续版本必须使用相同密钥，不能重新生成。

发布新版时提高 AndroidManifest 的 versionCode/versionName，构建签名 APK，更新 `discrete-math/version.json` 的 android 版本、APK URL、SHA-256 和大小，再提交到 Pages。不同签名无法覆盖安装。

## 验证边界

已进行 Java 编译、DEX 打包、资源清单/最低版本检查、APK 签名校验，以及版本比较/来源校验/下载路径测试。当前环境没有 Android 设备/模拟器，系统文件选择、安装流程、前后台生命周期和触屏视觉尚未做实机验收。
