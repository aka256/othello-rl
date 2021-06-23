# othello-rl

## Overview

MinecraftのDatapackで、強化学習によって作成されたオセロAIを動かせないかとの考えから試行錯誤をしている。
基本的な方針として以下のような流れを考えている。

- Minecraft外で強化学習(Q-Learning)
- 学習結果をStorageに保存
- Datapackから盤面に応じた選択を実行

## References

- Qiita, オセロをビットボードで実装する, <https://qiita.com/sensuikan1973/items/459b3e11d91f3cb37e43>
- オセロ・リバーシプログラミング講座 ～勝ち方・考え方～, オセロ（リバーシ）の作り方（アルゴリズム） ～石の位置による評価～, <https://uguisu.skr.jp/othello/5-1.html>
- prime's diary, Delta swapとその応用 【ビット演算テクニック Advent Calendar 2016 3日目】, <https://primenumber.hatenadiary.jp/entry/2016/12/03/203823>
- Chess Programming Wiki, Flipping Mirroring and Rotating, <https://www.chessprogramming.org/Flipping_Mirroring_and_Rotating>
