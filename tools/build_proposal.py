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

    body.append(heading(0, "專題名稱：AOOP_Final_Project_Group_1"))
    body.append(heading(1, "小組成員：第 1 組"))
    body.append(paragraph("劉育麟 112511002　張倖嘉 112511004　譚羽良 112511017"))
    body.append(heading(2, "專題動機與目標"))
    body.append(paragraph(
        "我們希望製作一款動作遊戲，結合角色操作、遊戲互動與視聽回饋，提供完整的遊玩體驗。"
        "透過遊戲開發，練習物件導向的設計與團隊協作。"
    ))
    body.append(paragraph(
        "本專題採用 Godot 與 GDScript，以既有個人原型為基礎，將遊戲功能劃分為不同模組，"
        "使程式便於維護與後續擴充。"
        "既有程式與課程期間新增的工作分別記錄，本專題僅用於 AOOP 課程繳交。"
    ))
    body.append(heading(3, "核心功能與範圍"))
    for text in [
        "遊戲邏輯：處理角色操作、遊戲互動與流程控制。",
        "介面與選單：提供遊戲資訊顯示與操作介面。",
        "音效系統：配合遊戲事件提供聲音回饋。",
        "資料管理：管理遊戲設定與進度資料。",
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
    docpr.set("descr", "遊戲系統分為遊戲邏輯、介面與選單、音效系統及資料管理四個主要模組。")
    diagram = paragraph("", keep=True)
    etree.SubElement(diagram, tag("r")).append(drawing)
    body.append(diagram)
    body.append(paragraph("圖 1　遊戲系統與主要模組。"))
    body.append(heading(6, "物件導向設計說明："))
    for text in [
        "封裝：各類別管理自己的資料與行為，透過明確的介面與其他物件互動。",
        "繼承與多型：將相近物件的共用行為抽出，讓不同物件可在相同的使用方式下呈現各自的行為。",
        "模組合作：遊戲邏輯、介面、音效與資料管理各自負責不同功能，透過事件或方法交換資訊，"
        "降低彼此依賴，方便分工與擴充。",
    ]:
        body.append(paragraph(text))
    body.append(heading(7, "成員分工"))
    for text in [
        "張倖嘉 Michelle／112511004：UI 與選單的設計、實作與整合。",
        "劉育麟 Jasper／112511002：SFX 音效的整理、播放功能與整合。",
        "譚羽良／112511017：遊戲操作、戰鬥邏輯與系統整合。",
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
    link.append(run("https://github.com/MoobyMoo/AOOP_Final_Project_Group_1"))
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
        {"Id": "rIdAOOPRepository", "Type": R + "/hyperlink", "Target": "https://github.com/MoobyMoo/AOOP_Final_Project_Group_1", "TargetMode": "External"},
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
        for required in ["112511002", "112511004", "112511017", "Michelle", "Jasper", "SFX", "介面與選單", "Godot", "GDScript"]:
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
