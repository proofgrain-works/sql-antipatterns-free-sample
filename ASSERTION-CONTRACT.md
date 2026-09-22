# Assertion contract

rows_v1は型を区別します。期待値が非空の二重配列なら行配列と照合します。それ以外は、結果が一行なら平坦な行、残りの一列結果は平坦な列、それ以外は行配列と照合します。空結果は[]です。eqp_semantics_v1はSCAN/SEARCH、table、index、range条件を照合します。

schema.sqlはassertion用fixtureです。bad.sql/good.sqlは参照snippetで、単純な連続実行手順ではありません。別のclean databaseでの操作はrun_scenarios.pyで検証します。DBはmemory内だけです。

Proofgrain Works — 実行して学ぶSQLアンチパターン：5ケース — 0.3.0
公開元: https://github.com/proofgrain-works/sql-antipatterns-free-sample
解説はCC BY 4.0、コード・実行fixtureはMIT。再利用時は適用noticeを保持し、解説を改変した場合は変更したことを表示してください。
