#!/usr/bin/env python3
"""Fill the retained AOOP DOCX template, preserving unrelated package parts."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
import subprocess

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs/templates/AOOP_Final_Project_Proposal_第X組.docx"
OUTPUT = ROOT / "docs/AOOP_Final_Project_Proposal_第1組.docx"
ASSETS = ROOT / "docs/assets"
QA = ROOT / "work/proposal-template-2026-11-08/qa"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W}


def tag(local):
    return f"{{{W}}}{local}"


def main():
    ASSETS.mkdir(exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=240", str(ASSETS / "proposal-architecture.dot"),
         "-o", str(ASSETS / "proposal-architecture.png")], check=True
    )
    with ZipFile(REFERENCE) as archive:
        original = {item.filename: archive.read(item) for item in archive.infolist()}
        infos = archive.infolist()

    document = etree.fromstring(original["word/document.xml"])
    body = document.find("w:body", NS)
    source = body.findall("w:p", NS)
    section = deepcopy(body.find("w:sectPr", NS))
    body_run = deepcopy(source[5].find("w:r/w:rPr", NS))
    color = body_run.find("w:color", NS)
    if color is not None:
        color.attrib.clear()
        color.set(tag("val"), "000000")

    def run(text, props=body_run):
        node = etree.Element(tag("r"))
        node.append(deepcopy(props))
        text_node = etree.SubElement(node, tag("t"))
        text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        text_node.text = text
        return node

    def paragraph(text, keep=False):
        node = etree.Element(tag("p"))
        props = deepcopy(source[0].find("w:pPr", NS))
        for item in list(props):
            if item.tag == tag("rPr"):
                props.remove(item)
        if keep:
            etree.SubElement(props, tag("keepNext"))
        node.append(props)
        node.append(run(text))
        return node

    def heading(index, label, page_break=False):
        node = deepcopy(source[index])
        for item in list(node):
            if item.tag != tag("pPr"):
                node.remove(item)
        props = node.find("w:pPr", NS)
        for inherited_color in props.findall("w:rPr/w:color", NS):
            inherited_color.attrib.clear()
            inherited_color.set(tag("val"), "000000")
        etree.SubElement(props, tag("keepNext"))
        if page_break:
            etree.SubElement(props, tag("pageBreakBefore"))
        heading_props = deepcopy(source[index].find("w:r/w:rPr", NS))
        c = heading_props.find("w:color", NS)
        if c is not None:
            heading_props.remove(c)
        node.append(run(label, heading_props))
        return node

    for item in list(body):
        body.remove(item)

    body.append(heading(0, "專題名稱：Cappuccino Assassino: Last Order"))
    body.append(heading(1, "小組成員：第 1 組"))
    body.append(paragraph("劉育麟 112511002　張倖嘉 112511004　譚羽良 112511017"))
    body.append(heading(2, "專題動機與目標"))
    body.append(paragraph(
        "我們希望製作一款第三人稱動作遊戲，讓玩家透過觀察 Boss 的攻擊前兆，"
        "掌握移動、閃避與反擊時機。玩家扮演人類劍士，Cappuccino Assassino 是故事中的宿敵。"
    ))
    body.append(paragraph(
        "本專題採用 Godot 與 GDScript，以既有個人原型為基礎，整理戰鬥、介面與音效的物件責任。"
        "課程成果將展示可替換的 Boss 行為、獨立的 UI 與音效模組，以及能完整遊玩的展示流程。"
        "既有程式與課程期間新增的工作分別記錄，本專題僅用於 AOOP 課程繳交。"
    ))
    body.append(heading(3, "核心功能與範圍"))
    for text in [
        "戰鬥與 Boss：玩家移動、攻擊與閃避；目標以兩種 Boss 行為展示共用戰鬥流程。",
        "UI 與選單：主選單、暫停、設定、生命值 HUD、勝利／失敗畫面與重試操作。",
        "音效系統：攻擊、命中、受傷、閃避、Boss 提示及選單回饋，並提供音量控制。",
        "進度與整合：儲存通關紀錄，串接選單、探索區、Boss 戰與結果畫面。",
    ]:
        body.append(paragraph(text))
    body.append(heading(4, "系統架構與程式骨幹"))
    body.append(heading(5, "系統架構圖："))

    # Transfer only an inline drawing from a temporary python-docx object.
    # Preserve the retained template's remaining XML and package parts.
    from docx import Document
    from docx.shared import Inches
    temporary = Document()
    image_run = temporary.add_paragraph().add_run()
    image_run.add_picture(str(ASSETS / "proposal-architecture.png"), width=Inches(5.7))
    drawing = deepcopy(image_run._r.find(tag("drawing")))
    drawing.xpath(".//*[local-name()='blip']")[0].set(f"{{{R}}}embed", "rIdAOOPArchitecture")
    docpr = drawing.xpath(".//*[local-name()='docPr']")[0]
    docpr.set("descr", "場景控制協調戰鬥、進度、UI與選單；戰鬥使用Boss行為物件；戰鬥與UI將事件送至音效模組。")
    diagram = paragraph("", keep=True)
    etree.SubElement(diagram, tag("r")).append(drawing)
    body.append(diagram)
    body.append(paragraph("圖 1　模組關係草案。箭頭表示呼叫或事件傳遞方向。"))
    body.append(heading(6, "物件導向設計說明："))
    for text in [
        "封裝與責任劃分：Combat 管理生命值、命中與戰鬥流程；Progression 管理通關與存檔；"
        "UI 模組處理畫面與操作；AudioDirector 管理音效事件與播放。",
        "組合與多型：Combat 持有 Encounter 行為物件，透過 definition、reset、step_boss 等共用方法"
        "使用不同 Boss。新增 Boss 時實作相同約定，並檢查必要方法與資料格式。",
        "繼承與事件：場景與 UI 使用 Node3D、Control，戰鬥資料使用 RefCounted；"
        "以訊號或明確的事件入口通知介面與音效，減少不同模組直接修改彼此狀態。",
        "可維護性：UI 與音效共用設定介面，按鈕調整音量後由播放系統套用。"
        "分別驗證畫面切換、音效事件、暫停與重試，避免一項修改破壞整段遊戲流程。",
    ]:
        body.append(paragraph(text))
    body.append(heading(7, "成員分工", page_break=True))
    for text in [
        "張倖嘉 Michelle／112511004：UI 與選單。負責主選單、暫停、設定、HUD、勝敗畫面；"
        "撰寫按鈕事件、畫面切換與設定控制程式，驗證顯示同步及重試流程。",
        "劉育麟 Jasper／112511002：SFX 與音效播放。整理音效來源與授權，建立事件對照，"
        "實作播放觸發、音量與優先序；處理暫停、重複觸發及重試時的清理，並驗證提示時機。",
        "譚羽良／112511017：玩家與 Boss 戰鬥、進度存檔及整合。定義模組事件與資料介面，"
        "協助 UI、音效接入戰鬥，負責可重現的展示版本與整合驗證。",
    ]:
        body.append(paragraph(text))
    body.append(paragraph(
        "三人各自提交實質程式與驗證紀錄，共同完成架構說明與展示。既有原型保留原作者紀錄，"
        "課程貢獻以各自新增或修改的工作說明。"
    ))
    body.append(heading(8, "Repo 連結"))
    link_para = paragraph("")
    link = etree.SubElement(link_para, tag("hyperlink"))
    link.set(f"{{{R}}}id", "rIdAOOPRepository")
    link.append(run("https://github.com/MoobyMoo/AOOP-Last-Order"))
    body.append(link_para)
    body.append(paragraph(
        "Repo 已公開。目前收錄提案與組員資料，後續加入可公開的課程程式與操作說明。"
        "組員持續以自己的帳號記錄工作，提交內容與分工對應。"
    ))
    body.append(section)

    rels = etree.fromstring(original["word/_rels/document.xml.rels"])
    package_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    for attrs in [
        {"Id": "rIdAOOPArchitecture", "Type": R + "/image", "Target": "media/aoop-architecture.png"},
        {"Id": "rIdAOOPRepository", "Type": R + "/hyperlink", "Target": "https://github.com/MoobyMoo/AOOP-Last-Order", "TargetMode": "External"},
    ]:
        etree.SubElement(rels, f"{{{package_ns}}}Relationship", **attrs)
    types = etree.fromstring(original["[Content_Types].xml"])
    ct_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    if not any(n.get("Extension") == "png" for n in types):
        etree.SubElement(types, f"{{{ct_ns}}}Default", Extension="png", ContentType="image/png")
    changed = {
        "word/document.xml": document,
        "word/_rels/document.xml.rels": rels,
        "[Content_Types].xml": types,
    }
    content = dict(original)
    for name, xml in changed.items():
        content[name] = etree.tostring(xml, xml_declaration=True, encoding="UTF-8", standalone=True)
    with ZipFile(OUTPUT, "w") as archive:
        for info in infos:
            archive.writestr(info, content[info.filename])
        archive.writestr("word/media/aoop-architecture.png", (ASSETS / "proposal-architecture.png").read_bytes())

    with ZipFile(OUTPUT) as final:
        for name, data in original.items():
            if name not in changed:
                assert final.read(name) == data, f"Preserve-only part changed: {name}"
        assert etree.tostring(etree.fromstring(final.read("word/document.xml")).find("w:body/w:sectPr", NS)) == etree.tostring(section)
        final_text = "".join(etree.fromstring(final.read("word/document.xml")).xpath(".//w:t/text()", namespaces=NS))
        for forbidden in ["簡述為什麼", "請附上", "請簡述", "務必注意", "1112511004"]:
            assert forbidden not in final_text, forbidden
        for required in ["112511002", "112511004", "112511017", "Michelle", "Jasper", "SFX", "主選單", "暫停", "Godot", "GDScript"]:
            assert required in final_text, required
    report = {"reference_sha256": sha256(REFERENCE.read_bytes()).hexdigest(),
              "output_sha256": sha256(OUTPUT.read_bytes()).hexdigest(),
              "unchanged_parts": len(original) - len(changed),
              "changed_parts": list(changed), "added_parts": ["word/media/aoop-architecture.png"],
              "section_geometry_preserved": True, "slot_coverage": "pass", "placeholders_removed": True}
    (QA / "package-fidelity.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
