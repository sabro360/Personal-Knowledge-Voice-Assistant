"""T1704 Knowledge生成結果確認スクリプト。

11件の日本語会話シナリオで OpenAIKnowledgeModel の出力品質を確認する。
自動テストスイートには含まない手動検証ツール。

Usage:
    cd backend
    uv run python scripts/verify_knowledge.py

Requires:
    OPENAI_API_KEY environment variable (or set in .env)
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.providers.errors import KnowledgeExtractionError
from app.providers.knowledge_extraction_schema import KnowledgeExtraction
from app.providers.openai_knowledge_model import OpenAIKnowledgeModel


@dataclass
class _Speaker:
    """Minimal speaker object satisfying the speaker.value interface."""

    value: str


@dataclass
class _Utt:
    """Minimal utterance object for use with _format_transcript()."""

    speaker: _Speaker
    text: str


def u(speaker: str, text: str) -> _Utt:
    """Create a minimal utterance."""
    return _Utt(speaker=_Speaker(value=speaker), text=text)


# ---------------------------------------------------------------------------
# 11 verification scenarios
# ---------------------------------------------------------------------------
SCENARIOS: list[dict] = [
    {
        "name": "01 CDが虹色な理由 + 派生質問",
        "note": "T1703検証: related_questionsに派生質問が入るか",
        "utterances": [
            u("user", "CDってなんで虹色に見えるの？"),
            u("assistant", "CDの表面には非常に細かい溝が螺旋状に刻まれていて、光が当たると波長ごとに異なる角度で反射する「回折」という現象が起きます。これにより虹色に見えるんです。"),
            u("user", "水滴で虹ができるのとは違う仕組みなの？"),
            u("assistant", "そうですね。虹は水滴の中で光が屈折・反射して波長ごとに分かれるのが原因です。CDは回折格子による回折が原因なので、仕組みは異なります。どちらも光の分散ですが、メカニズムが違います。"),
        ],
    },
    {
        "name": "02 飛行機が飛ぶ仕組み",
        "note": "単一トピック・物理",
        "utterances": [
            u("user", "飛行機ってどうやって空を飛べるの？"),
            u("assistant", "飛行機の翼は断面が上側が膨らんだ非対称な形になっています。空気が翼の上下を流れると、上側の方が速く流れ、気圧が下がります。この気圧差が揚力を生み、飛行機を持ち上げます。"),
            u("user", "それってベルヌーイの定理のこと？"),
            u("assistant", "はい、そのとおりです。ベルヌーイの定理では流体の速度が増すと圧力が下がるとされており、翼の上下の圧力差が揚力の主な原因の一つです。"),
        ],
    },
    {
        "name": "03 コーヒーと眠気の関係",
        "note": "単一トピック・生物化学",
        "utterances": [
            u("user", "コーヒーを飲むと眠気が覚めるのはなぜ？"),
            u("assistant", "コーヒーに含まれるカフェインが、脳内で眠気を引き起こす物質「アデノシン」の受容体に結合します。するとアデノシンが受容体に届かなくなり、眠気が感じにくくなります。"),
            u("user", "カフェインの効果はどれくらい続く？"),
            u("assistant", "個人差はありますが、カフェインの半減期は約5〜6時間です。つまり飲んでから5〜6時間後にも体内にカフェインの半量が残っている計算になります。"),
        ],
    },
    {
        "name": "04 Pythonのリストとタプルの違い",
        "note": "単一トピック・IT",
        "utterances": [
            u("user", "Pythonのリストとタプルって何が違うの？"),
            u("assistant", "最大の違いはミュータビリティです。リストは要素の追加・削除・変更が可能な「可変」なオブジェクトです。タプルは一度作ると変更できない「不変」なオブジェクトです。"),
            u("user", "じゃあタプルはどんな時に使えばいい？"),
            u("assistant", "変更してほしくないデータに使います。たとえばRGB色の値 (255, 0, 0) や座標 (35.6, 139.7) など、意味的に変わらない値の組み合わせに向いています。また辞書のキーにはリストは使えませんがタプルは使えます。"),
        ],
    },
    {
        "name": "05 株価が変動する理由",
        "note": "単一トピック・経済",
        "utterances": [
            u("user", "株価ってなんで毎日変わるの？"),
            u("assistant", "株価は基本的に需要と供給で決まります。その企業の業績や将来性に期待する投資家が増えれば買いが集まり株価が上がります。逆に悪材料が出れば売りが増えて下がります。"),
            u("user", "ニュースで株が動くのはなんで？"),
            u("assistant", "ニュースが投資家の期待や不安に影響するからです。たとえば好決算のニュースは「この会社は儲かっている」という期待を高めて買いを誘い、不祥事は信頼を下げて売りを誘います。"),
        ],
    },
    {
        "name": "06 虹の色の数 ＋ 蜃気楼の仕組み",
        "note": "T1702検証: 複数トピックが別々のKnowledgeに分割されるか",
        "utterances": [
            u("user", "虹って7色って言うけど本当に7色なの？"),
            u("assistant", "実は虹の色に明確な境界はなく、連続したスペクトルです。赤から紫まで無数の色が連続しています。日本で「7色」と言うのは、ニュートンが音楽の7音に合わせて7つに区切ったことが由来とされています。"),
            u("user", "そういえば蜃気楼ってどういう仕組みなの？"),
            u("assistant", "蜃気楼は光の屈折によって起きます。地面近くの空気が熱せられると、温度の違いによって空気の密度差が生まれます。光はこの密度差のある空気の層を通ると屈折し、本来とは違う場所に像が見えるのが蜃気楼です。"),
        ],
    },
    {
        "name": "07 電子レンジの仕組み + 派生質問",
        "note": "T1703検証: related_questionsに金属の質問が入るか",
        "utterances": [
            u("user", "電子レンジはどうやって食べ物を温めるの？"),
            u("assistant", "電子レンジはマイクロ波という電磁波を使います。マイクロ波が食品中の水分子を振動させ、その摩擦熱で食品内部から温まります。だから外側だけでなく内部も同時に加熱できます。"),
            u("user", "なんで金属を入れると危ないの？"),
            u("assistant", "金属はマイクロ波を反射するため、電磁波が金属の表面や端部に集中します。すると電流が流れて火花が発生したり、最悪の場合は火災や故障の原因になります。"),
        ],
    },
    {
        "name": "08 夢を見る仕組み",
        "note": "単一トピック・神経科学",
        "utterances": [
            u("user", "夢ってなんで見るの？"),
            u("assistant", "夢は主にREM睡眠中に起きます。REM睡眠では脳が活発に活動していて、記憶の整理・定着が行われると考えられています。夢はその記憶処理の過程で生じる副産物という説が有力です。"),
            u("user", "怖い夢をよく見るんだけどなんで？"),
            u("assistant", "ストレスや不安が多いと、脳がネガティブな記憶や感情を処理しようとするため、悪夢を見やすくなると言われています。また睡眠の質が低い時にも起きやすいです。"),
        ],
    },
    {
        "name": "09 植物の光合成",
        "note": "単一トピック・植物生物学",
        "utterances": [
            u("user", "植物はなんで光合成ができるの？"),
            u("assistant", "植物の細胞にはクロロフィルという緑色の色素を含む「葉緑体」があります。クロロフィルが太陽の光エネルギーを吸収し、二酸化炭素と水からブドウ糖と酸素を作ります。これが光合成です。"),
            u("user", "夜は光合成しないの？"),
            u("assistant", "はい、光合成には光エネルギーが必要なので夜間は行いません。ただし植物は昼夜問わず「呼吸」はしています。呼吸は酸素を使ってエネルギーを取り出す、光合成とは逆の反応です。"),
        ],
    },
    {
        "name": "10 ブラックホールとは",
        "note": "単一トピック・天文学",
        "utterances": [
            u("user", "ブラックホールって何なの？"),
            u("assistant", "ブラックホールは重力が非常に強く、光でさえ脱出できない天体です。質量が大きな星が寿命を迎えて重力崩壊すると生まれます。「事象の地平面」という境界の内側からは何も出てこられません。"),
            u("user", "ブラックホールに吸い込まれたらどうなるの？"),
            u("assistant", "ブラックホールに近づくほど重力差が大きくなり、足と頭にかかる重力が全く異なるため、体が縦に引き伸ばされる「スパゲッティ化」が起きます。事象の地平面を越えた後は外に出る方法はありません。"),
        ],
    },
    {
        "name": "11 塩がしょっぱい理由（短い1往復）",
        "note": "エッジケース: 最短会話でも正しく抽出できるか",
        "utterances": [
            u("user", "塩ってなんでしょっぱいの？"),
            u("assistant", "塩（塩化ナトリウム）が水に溶けるとナトリウムイオンと塩化物イオンに分かれます。ナトリウムイオンが舌の味蕾にある塩味受容体に結合することで、しょっぱさを感じます。"),
        ],
    },
]


def _print_separator(char: str = "=", width: int = 60) -> None:
    print(char * width)


def run_scenario(model: OpenAIKnowledgeModel, scenario: dict) -> bool:
    """Run one scenario through the model and print results. Return True on success."""
    _print_separator()
    print(f"シナリオ {scenario['name']}")
    print(f"目的     : {scenario['note']}")
    _print_separator()

    try:
        items: list[KnowledgeExtraction] = model.extract_knowledge(scenario["utterances"])
    except KnowledgeExtractionError as exc:
        print(f"FAILED: {exc}")
        return False

    for i, item in enumerate(items, start=1):
        print(f"[Knowledge {i}/{len(items)}]")
        print(f"  title    : {item.title}")
        print(f"  question : {item.question}")
        print(f"  summary  : {item.summary}")
        print(f"  answer   : {item.answer}")
        print(f"  category : {item.category}")
        print(f"  keywords : {item.keywords}")
        print(f"  related  : {item.related_questions}")
        if i < len(items):
            print()

    print()
    print(f"PASS ({len(items)} item{'s' if len(items) != 1 else ''})")
    return True


def main() -> None:
    """Run all verification scenarios and print a summary."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        print("       Set it in your shell or in backend/.env before running.")
        sys.exit(1)

    model = OpenAIKnowledgeModel(api_key=api_key)

    passed = 0
    failed = 0

    for scenario in SCENARIOS:
        print()
        success = run_scenario(model, scenario)
        if success:
            passed += 1
        else:
            failed += 1
        _print_separator("-")

    print()
    _print_separator()
    print("結果サマリー")
    _print_separator()
    print(f"  合計    : {len(SCENARIOS)} シナリオ")
    print(f"  PASS    : {passed}")
    print(f"  FAIL    : {failed}")
    _print_separator()


if __name__ == "__main__":
    main()
