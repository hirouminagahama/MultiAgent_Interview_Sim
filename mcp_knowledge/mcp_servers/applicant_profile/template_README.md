以下は、今後「背景記述」を追加していくための **`career_background.json` 入力テンプレート（空の雛形）** です。
前回示した柔軟構造（`project_details`・`individual_initiatives`・`reflection_and_thoughts`）をすべて保持しつつ、
どの部署にも使える汎用形式にしています。

---

## 🧩 `career_background_template.json`

```json
{
    "career_details": [
        {
            "department": "（所属部署名を記入）",
            "position": "（役職を記入）",
            "period": "（在籍期間を記入）",
            "project_details": [
                {
                    "project": "（プロジェクト名を記入）",
                    "intent": "（このプロジェクトを行った目的・意図）",
                    "execution": [
                        "（実行内容1）",
                        "（実行内容2）",
                        "（実行内容3）"
                    ],
                    "results": "（定量・定性的な成果）",
                    "reflection": "（得た学び・気づき・価値観の変化など）"
                }
            ],
            "individual_initiatives": [
                {
                    "topic": "（個人で取り組んだ活動のテーマ）",
                    "description": "（その取り組みの内容・工夫・背景）"
                }
            ],
            "reflection_and_thoughts": {
                "learning": "（この期間全体で学んだこと）",
                "influence": "（この経験が後のキャリアにどう影響したか）"
            }
        },
        {
            "department": "（次の部署名）",
            "position": "（役職）",
            "period": "（在籍期間）",
            "project_details": [],
            "individual_initiatives": [],
            "reflection_and_thoughts": {}
        },
        {
            "meta_background": {
                "motivation": "（キャリア全体を通じた動機）",
                "philosophy": "（仕事・技術に対する信念や価値観）",
                "career_vision": "（今後のキャリアビジョンや目指す方向）",
                "personal_notes": "（全体に関する自由記述・補足）"
            }
        }
    ]
}
```

---

## 🧭 書き方のコツ

| セクション                     | 記載の目的           | 記入のヒント                                |
| ------------------------- | --------------- | ------------------------------------- |
| `project_details`         | 明確なプロジェクトの背景や狙い | 「なぜその取り組みをしたのか」→「どう実行したのか」→「何を得たか」で構成 |
| `individual_initiatives`  | プロジェクト外の主体的活動   | チーム文化形成・勉強会・ツール導入・他部署連携などを記載          |
| `reflection_and_thoughts` | 期間全体での成長や考え方の変化 | 「抽象的な学び」や「自分なりの哲学」を書く                 |
| `meta_background`         | 全キャリア共通の信念・方向性  | LLMが“人格・軸”を理解できるような自己観を整理             |

---

## 💡 活用例（記入イメージ）

```json
{
    "career_details": [
        {
            "department": "ICT本部 システム開発部",
            "position": "主任",
            "period": "2022年4月〜2024年3月",
            "project_details": [
                {
                    "project": "AIモデル運用基盤構築",
                    "intent": "工場のAI活用を継続的に支える仕組みを作るため。",
                    "execution": [
                        "SageMakerを用いたモデル再学習パイプラインを設計。",
                        "推論結果をRedshiftに蓄積し、品質モニタリングを自動化。"
                    ],
                    "results": "AIモデルの更新工数を50%削減。",
                    "reflection": "技術導入よりも“運用を設計する力”の重要性を痛感した。"
                }
            ],
            "individual_initiatives": [
                {
                    "topic": "GitLab導入とアジャイル開発推進",
                    "description": "属人化していた開発体制を刷新。GitLabによるコードレビュー体制を導入し、スクラム的な開発リズムを確立した。"
                },
                {
                    "topic": "チーム教育活動",
                    "description": "社内勉強会を定期開催し、部内メンバーのPython・SQLスキル底上げを実施。"
                }
            ],
            "reflection_and_thoughts": {
                "learning": "チームで成果を出すためには、技術力だけでなく“共通言語づくり”が必要。",
                "influence": "後のAIエージェント導入構想でのチーム設計思想につながった。"
            }
        },
        {
            "meta_background": {
                "motivation": "ものづくりとデータ分析を融合し、現場の知を支えるAIを広めること。",
                "philosophy": "AI導入とは“現場の意思決定を支援する仕組みづくり”である。",
                "career_vision": "チーム単位で改善を進める仕組みを設計・運営できるリーダーを目指す。",
                "personal_notes": "技術と組織を両輪で考える力を、今後も磨き続けたい。"
            }
        }
    ]
}
```


