# Cappuccino Assassino: Last Order

AOOP 2026 Fall 第 1 組期末專題。以 Godot 與 GDScript 製作第三人稱動作遊戲，透過戰鬥模擬、Boss 行為、進度儲存與介面模組呈現物件導向設計。

玩家是自訂的人類劍士，也是組織最後的劍士。Cappuccino Assassino 是 Boss／宿敵；遊戲名稱沿用 Cappuccino Assassino: Last Order。

## 組員

| 姓名 | 學號 | GitHub |
| --- | --- | --- |
| 劉育麟 Jasper | 112511002 | [jasper209405](https://github.com/jasper209405) |
| 張倖嘉 Michelle | 112511004 | [michelle-151027](https://github.com/michelle-151027) |
| 譚羽良 | 112511017 | [MoobyMoo](https://github.com/MoobyMoo) |

## 提案與繳交

- [期末專題提案 PDF](docs/AOOP_Final_Project_Proposal_第1組.pdf)
- [可編輯 Word 提案](docs/AOOP_Final_Project_Proposal_第1組.docx)
- [提案補充說明](docs/proposal.md)
- [組員資料來源](docs/team.md)
- 截止時間：2026 年 11 月 16 日星期一 23:59，由組長繳交。
- 繳交檔名：`AOOP_Final_Project_Proposal_第1組.pdf`，內容須附公開 Repo 連結。
- Repo：https://github.com/MoobyMoo/AOOP-Last-Order

提案已套用助教提供的 Word 範本，包含系統架構圖與組員分工。繳交前由組內確認內容與繳交人。

## 分工

- 張倖嘉 Michelle：UI 與選單，包含主選單、暫停、設定、HUD 與勝敗畫面。
- 劉育麟 Jasper：SFX 與音效播放，包含事件觸發、音量設定、優先序及暫停／重試處理。
- 譚羽良：玩家與 Boss 戰鬥、進度存檔及整合。

## 專案狀態

此 Repo 保留原 AOOP-project 的歷史及組員權限，目前包含提案與組員資料，尚未匯入遊戲程式，也沒有可在此直接執行的版本。既有遊戲的開發暫停決定不因本次文件整理而改變。

本專題只用於 AOOP 課程繳交。提案如使用先前已存在的個人遊戲原型，須註明既有範圍及本課程新增的工作，不將舊有工作列為組員的新貢獻。

## 協作方式

每項工作先開 Issue，寫明預期行為與驗收方式。組員以自己的 GitHub 帳號在分支提交實質修改，再透過 Pull Request 說明變更與驗證結果。不要產生空白 Commit、代替他人署名，或為增加次數而拆分無意義提交。

課程會參考 Commit 紀錄與分工貢獻，請從實際開始工作時持續提交。AI 可以協助開發；每位組員仍須能解釋自己提交的設計與程式。
