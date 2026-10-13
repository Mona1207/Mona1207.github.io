# UI 更新：设计稿参考版 V8

此次更新调整首页、知识树、答题、设置及二级页面，统一为暖白背景、薄荷绿主色、浅黄解析卡和圆润按钮。底部保留知识树、首页、设置三个入口。

主布局以 390px 逻辑视口为基准：手机外边距 13px，卡片圆角 24–26px，底栏 56px 加设备安全区，主按钮 48–51px，内容长度按真实教材自适应。

答题提交前隐藏答案；点击下一题时先保存自评；自评失败时保留当前题；笔记在题目页编辑，汇总页可查询。知识树显示章节到知识点的分支，原教材章、节、小节层级仍保留在全书框架。

## 验证

- 前端 11 个测试文件、77 项测试通过。
- TypeScript 与生产构建通过。
- 未完成手机实机截图对照，不能据此宣称逐像素一致。

## 插画素材与生成说明

网站未公开上传用户提供的原始参考图片；当前使用独立素材。

- 看书兔子：illustrations/reading-bunny-v6.webp，沿用网站已有素材。
- 教材书本：illustrations/study-books-v7.webp，沿用网站已有素材。
- 太阳：illustrations/sun-v8.png，以内置 imagegen 生成，没有提供任何参考图片作为输入。

太阳生成提示词：

> Original transparent PNG illustration for a personal learning website. A friendly butter-yellow rounded sunshine character with eight small rounded rays, tiny dark brown oval eyes, a smiling mouth, subtle peach blush and small soft white mitten hands. One hand gently points upwards as an idea cue. Polished soft 3D clay illustration, warm diffuse lighting, legible at 60px. Palette: butter yellow #FFDF68, pale gold, cream white and soft peach. Whole character centered, no cropping. No text, interface, screenshots, logos or watermark. Transparent alpha background.

