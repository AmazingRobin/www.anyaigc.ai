# Seedance 专题页数据说明

核对日期：2026-11-05。站内 slug 统一小写：`seedance`，四个型号页沿用需求中的 `doubao-seedance-*`。

价格来自 [AnyAIGC 模型广场](https://anyaigc.ai/pricing?keyword=seedance)的模型详情抽屉，单位全部是 USD / 1M tokens。用户于 2026-11-05 确认统一展示 Fast / mini 的最低一套价格，页面不显示令牌分组名称。

| 型号 | AnyAIGC model |
| --- | --- |
| Seedance 2.5 | `doubao-seedance-2-5-260628` |
| Seedance 2.0 | `doubao-seedance-2-0-260128` |
| Seedance 2.0 Fast | `doubao-seedance-2-0-fast-260128` |
| Seedance 2.0 mini | `doubao-seedance-2-0-mini-260615` |

请求路径均由模型广场确认：`POST /api/v3/contents/generations/tasks`。

## 用户确认的接口事实（2026-11-05）

1. Fast 最低价格为不含视频输入 $4.914、含视频输入 $2.896 / 1M tokens；mini 为 $3.071、$1.843 / 1M tokens。
2. Seedance 2.0 的 4K 当前可调用，单价为不含参考视频 $4.860、含参考视频 $2.916 / 1M tokens。示例继续使用 720p，页面与 FAQ 明确写明 4K 可用。
3. mini 使用相同的 `content[]` 请求结构，一次任务生成 1 条视频，所有用户默认享有不限并发。中英文 cURL / Python 示例均使用 mini 自己的模型名 `doubao-seedance-2-0-mini-260615`。

页面中的待确认提示已移除；公开文档缺少的上述说明以本次用户确认补足。

接口文档：

- [2.0 / Fast 创建任务](https://docs.anyaigc.ai/en/reference/seedance/post/api/v3/contents/generations/tasks?leaf=438503106)
- [2.0 查询任务](https://docs.anyaigc.ai/en/reference/volc/api/v3/contents/generations/tasks/%7Bid%7D?leaf=438503236)
- [2.5 创建任务](https://docs.anyaigc.ai/en/reference/seedance/post/api/v3/contents/generations/tasks?leaf=c%3A1792738852814)
- [2.5 查询任务](https://docs.anyaigc.ai/en/reference/seedance/api/v3/contents/generations/tasks/%7Bid%7D?leaf=c%3A1792739265091)

查询文档的成功示例明确使用 `status: "succeeded"`、`content.video_url`、`usage.completion_tokens` 和 `usage.total_tokens`。不推测其他状态枚举，Python 代码检查成功、错误对象和总等待超时；不进行付费生成测试。

## 再生成

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/seedance_pages.py
python scripts/seedance_register.py
python scripts/payments.py
python scripts/trust.py
python scripts/check_topics.py
# 先运行 python scripts/preview.py，再生成分享图
python scripts/og_seedance.py
```

品牌图标使用现有的 `bytedance-color.svg`（lobe-icons 固定 1.98.0）。官网风格参考的颜色为 `#f8f8f8`、`#eff0f3`、`#212121`，型号页首屏为深色电影感背景与白色半透明胶囊按钮；使用本地系统字体。按用户本次要求，首屏改用从模型官网获取的官方视频，替换原 CSS 抽象画面。


## 官方首屏素材（2026-11-05）

- `assets/models/seedance/seedance-2-0-official.mp4`：来自 [Seedance 2.0 官网](https://seed.bytedance.com/zh/seedance2_0)首屏，1280×720，约 10 秒，保留原音轨。用于 2.0 / Fast / mini 页面；后两者标明「系列能力参考」，不称为 Fast 或 mini 生成。
- `assets/models/seedance/seedance-2-5-official.mp4`：来自 [Seedance 2.5 官网](https://seed.bytedance.com/zh/seedance2_5)首屏，1280×720，约 30 秒。保留完整时长与音轨，H.264 / AAC 压缩到约 6.5 MB，用于总览与 2.5 页面。
- 对应 `.webp` 封面从视频帧提取，视频按原始 16:9 比例呈现，不裁切。
- 素材本地托管，页面显示来源与字节跳动版权说明；提供原生播放控件、内联播放，点击后播放，不自动播放。
