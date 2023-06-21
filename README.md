![Vectorworks Architect 2022 -  名称未設定 1  2023_06_16 20_51_38 (2)](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/assets/113188583/f81150b9-0bb6-4e10-a125-9bf2870501ac)

# Ladybug-tool for Vectorworks
ここは、grasshopper等で環境シミュレーションが出来るプラグインの**ladyubug tools** を**Vectorworksのマリオネット**に移植するプロジェクトページです。

(現在、
 - ladybug:lady_beetle: honeybee,honeybee-radiance,honeybee-energy:honeybee: を移植中である程度動くようになった段階です。今後、ほとんどのGrasshopperのコンポーネントをマリオネット・ノードに変換予定です。
 - 将来的には butterfly:butterfly: doragonfly ![6a51bd3aa8328fc803017009cd663f49](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/assets/113188583/5bafd2fa-a91d-4715-ac39-6501b537a4df) の移植にも挑戦予定です。

質問等は気軽に [**Discussions**](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/discussions) の方にお願いします。	:mailbox:

（協力していただける方がいれば歓迎です。ご連絡いただければ Discord への招待をお送りします。）

## インストール
（例）
```
python -m pip install ladybug-vectorworks
```
インストール後にインストールされた「ladybug_vectorworks」=>「etc」フォルダ内の **HowToInstall.pdf** 又は **HowToInstall.vwx** をご覧ください。
もしくは、[こちら](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/blob/main/ladybug_vectorworks/etc/HowToInstall.pdf)をご覧ください。

インストール後の「ladybug_vectorworks」=>「etc」フォルダ内には上記のインストール方法のpdf&vwx、ノード一覧(Node_list.vwx)、サンプルファイル(Ladybug-sample.vwx)が同梱されています。

管理者の環境により、Vectorworks2022でファイルを作成・動作テストを行っております。（vw2018も書き出していますが、動作テストは行っていません。）

また、[こちら](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/releases) より更新履歴を確認できます。

## Ladybug tools<sub> (参照元)</sub>
**Ladybug Tools** :lady_beetle:	は、環境に配慮した設計とシミュレーションをサポートする無料のコンピューター アプリケーションのコレクションです。


→ladybug tools : https://www.ladybug.tools/index.html
→ladybug tools(github) : https://github.com/ladybug-tools

------------------------------------------------------------------------------

## Ladybug-tool for Vectorworks

This is a project page for porting ladybug tools, a plug-in that can simulate environments with grasshopper, etc., to Vectorworks marionette.

(the current,

Ladybug🐞 honeybee,honeybee-radiance,honeybee-energy🐝 is now in the process of porting.

In the future, we plan to convert most Grasshopper components to marionette nodes.

In the future, we plan to try porting butterfly🦋 dragonfly ![6a51bd3aa8328fc803017009cd663f49](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/assets/113188583/5bafd2fa-a91d-4715-ac39-6501b537a4df).

Please feel free to ask questions to [Discussions](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/discussions). 📫

(Anyone who would like to help is welcome. Get in touch and he'll send you a Discord invite.)

### install
(example)
```
python -m pip install ladybug-vectorworks
```
Please see **HowToInstall.pdf** or **HowToInstall.vwx** in the "ladybug_vectorworks" => "etc" folder installed after installation.
Or see [here](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/blob/main/ladybug_vectorworks/etc/HowToInstall.pdf).

After installation, "ladybug_vectorworks" => "etc" folder contains pdf&vwx, node list (Node_list.vwx) and sample file (Ladybug-sample.vwx) for the above installation method.

We are creating and testing files with Vectorworks2022 in the administrator's environment. (I have also written vw2018, but I have not tested it.)

You can also check the update history [here](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/releases).

### Ladybug tools (source)
Ladybug Tools 🐞 is a collection of free computer applications that support green design and simulation.

→ladybug tools : https://www.ladybug.tools/index.html
→ladybug tools(github) : https://github.com/ladybug-tools
