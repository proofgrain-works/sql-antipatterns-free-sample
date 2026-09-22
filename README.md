# 実行して学ぶSQLアンチパターン：5ケース

表の値を見て、目的に合うSQLかを考える5ケースです。正しい構文でも、NULL、集計の単位、更新方法、探索条件、結合キーによって意図と違う結果になります。各ケースは入力表から始まり、期待結果とSQLを比較して読めます。

## まず読む

index.htmlをブラウザで開き、043→001→009→025→031の順に、入力表・目的と期待結果・仕組み・問い・SQLを確認してください。実行なしでも読めます。

## 任意の実行

任意の実行にはPython 3.11以上と、そのPythonが使うSQLite 3.53.4 exactが必要です。SQLite CLIだけのversion確認では足りません。最低Python条件は全Python版で検証済みという意味ではなく、その他のSQLite versionは未検証です。SQLite/Python binaryは同梱しません。

```sh
python3 -c 'import sys, sqlite3; print(sys.version_info[:3], sqlite3.sqlite_version)'
python3 -B run_assertions.py
python3 -B run_scenarios.py
```

有料版は検討中・価格未定です。販売、予約、投げ銭、通知登録、email収集は行いません。

Proofgrain Works — 実行して学ぶSQLアンチパターン：5ケース — 0.3.0
公開元: https://github.com/proofgrain-works/sql-antipatterns-free-sample
解説はCC BY 4.0、コード・実行fixtureはMIT。再利用時は適用noticeを保持し、解説を改変した場合は変更したことを表示してください。
