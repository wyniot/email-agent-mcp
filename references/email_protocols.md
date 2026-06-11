# Email Protocols Reference - IMAP & SMTP 指南

## IMAP（接收邮件）

### 常用服务器地址
- Gmail: imap.gmail.com (SSL, port 993)
- Outlook/Hotmail: outlook.office365.com (SSL, port 993)
- QQ邮箱: imap.qq.com (SSL, port 993)
- 163邮箱: imap.163.com (SSL, port 993)

### 常用命令
- LOGIN: 登录
- SELECT: 选择文件夹
- SEARCH: 搜索邮件 (UNSEEN, ALL, FROM "xxx")
- FETCH: 获取邮件内容
- LOGOUT: 退出

### 注意事项
- Gmail 需要"应用专用密码"而非登录密码
- 开启 IMAP 需要在邮箱设置中启用
- SEARCH 返回的是邮件 ID 列表

## SMTP（发送邮件）

### 常用服务器地址
- Gmail: smtp.gmail.com (SSL, port 465)
- Outlook: smtp.office365.com (STARTTLS, port 587)
- QQ邮箱: smtp.qq.com (SSL, port 465)
- 163邮箱: smtp.163.com (SSL, port 465)

### 注意事项
- Gmail 建议使用 SMTP_SSL
- 部分服务器使用 STARTTLS（先明文连接再加密）
- 发送前需登录认证

## 常见问题

1. 连接超时 - 检查防火墙和网络
2. 认证失败 - 确认用户名密码正确；Gmail 需应用专用密码
3. 编码问题 - 使用 RFC 2047 编码中文标题
4. SSL 错误 - 确保服务器地址和端口匹配
