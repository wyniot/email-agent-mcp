# API Setup Guide

## OpenAI API Key

1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 进入 API Keys 页面: https://platform.openai.com/api-keys
4. 点击 "Create new secret key"
5. 复制 key 并填入 .env 的 OPENAI_API_KEY 字段

费用: GPT-4 按 token 计费，新用户有 $5 免费额度

## Google Gemini API Key

1. 访问 https://aistudio.google.com/
2. 使用 Google 账号登录
3. 点击 "Get API Key"
4. 创建或选择项目，生成 API Key
5. 复制 key 并填入 .env 的 GEMINI_API_KEY 字段

费用: Gemini 有免费配额（每分钟60请求），超出后按量计费

## Gmail 应用专用密码

1. 开启两步验证: https://myaccount.google.com/security
2. 搜索 "App passwords" 或访问:
   https://myaccount.google.com/apppasswords
3. 选择应用: "Mail" + 设备: "Windows Computer"
4. 生成 16 位密码
5. 填入 .env 的 EMAIL_PASSWORD 字段（不是登录密码！）
