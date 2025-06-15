import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from entity.entity import Hand

logger = logging.getLogger(__name__)

generate_question_prompt_template = """
あなたは日本のリーチ麻雀の点数計算問題を作成する専門家です。下記のパラメータを組み合わせて、指定した文字列が答えになるような問題を作成してください。

## パラメータの説明:bool値以外のパラメータは全て必須です。
tilesは136形式の配列であり和了時の手牌です。14枚になります。14枚ではない場合入力として間違っています。例: ["1m", "2m", "3m", "4m", "4m", "5p", "5p", "5p", "7p", "8p", "9p", "1z", "1z", "1z"]
meldsは鳴きの情報を格納する配列です。鳴きは136形式の配列であり、それらが配列になっています。必ずtilesの中に含まれている牌で順子、刻子、槓子でなければなりません。例: [["1m", "2m", "3m"], ["4s", "4s", "4s"]]
win_tileは和了牌です。例: "1m"
dora_indicatorsはドラ表示牌のリストです。例: ["2m"]
is_riichiはリーチ宣言済みかどうかです。
is_tsumoは自摸和了かどうかです。
is_ippatsuは一発かどうかです。
is_rinshanは嶺上開花かどうかです。
is_chankanは槍槓かどうかです。
is_haiteiは海底摸月かどうかです。
is_houteiは河底撈魚かどうかです。
is_daburu_riichiはダブルリーチかどうかです。
is_nagashi_manganは流し満貫かどうかです。
is_tenhouは天和かどうかです。
is_chiihouは地和かどうかです。
is_renhouは人和かどうかです。
is_open_riichiはオープンリーチかどうかです。
player_windは自風です。
round_windは場風です。

## 手牌の表記方法
麻雀の手牌は136形式で表されます。萬子をm、筒子をp、索子をs、字牌をzで表します。各牌は4枚ずつあります。
1萬:1m, 2萬:2m, 3萬:3m, 4萬:4m, 5萬:5m, 6萬:6m, 7萬:7m, 8萬:8m, 9萬:9m
1筒:1p, 2筒:2p, 3筒:3p, 4筒:4p, 5筒:5p, 6筒:6p, 7筒:7p, 8筒:8p, 9筒:9p
1索:1s, 2索:2s, 3索:3s, 4索:4s, 5索:5s, 6索:6s, 7索:7s, 8索:8s, 9索:9s
東:1z, 南:2z, 西:3z, 北:4z, 白:5z, 發:6z, 中:7z

{format_instructions}

{query}
"""

class MahjongQuestionGenerator:
    def __init__(self, model, query_template: str = generate_question_prompt_template):
        self.model = model
        self.model_name = model.model_name if hasattr(model, "model_name") else model.model
        self.parser = JsonOutputParser(pydantic_object=Hand)
        self.query_template = query_template

    def generate_question(self, query: str) -> Dict[str, Any]:
        prompt = PromptTemplate(
            template=self.query_template,
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

        chain = prompt | self.model | self.parser
        return chain.invoke({"query": query})
