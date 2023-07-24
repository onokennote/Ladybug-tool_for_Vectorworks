![Vectorworks Architect 2022 -  名称未設定 1  2023_06_16 20_51_38 (2)](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/assets/113188583/f81150b9-0bb6-4e10-a125-9bf2870501ac)

# Ladybug-tool for Vectorworks
[![Downloads](https://static.pepy.tech/personalized-badge/ladybug-vectorworks?period=total&units=international_system&left_color=red&right_color=black&left_text=Downloads%20from%20PyPI)](https://pepy.tech/project/ladybug-vectorworks)

ここは、grasshopper等で環境シミュレーションが出来るプラグインの**ladyubug tools** を**Vectorworksのマリオネット**に移植するプロジェクトページです。

###### ladybug tools と ladybug tool が混在していますが、レポジトリ名を変えるのは控えてこのままいきます。

(現在、
 - ladybug:lady_beetle: honeybee,honeybee-radiance,honeybee-energy:honeybee: を移植中である程度動くようになった段階です。今後、ほとんどのGrasshopperのコンポーネントをマリオネット・ノードに変換予定です。
 - 将来的には butterfly:butterfly: doragonfly ![6a51bd3aa8328fc803017009cd663f49](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/assets/113188583/5bafd2fa-a91d-4715-ac39-6501b537a4df) の移植にも挑戦予定です。

質問等は気軽に [**Discussions**](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/discussions) の方にお願いします。	:mailbox:

（協力していただける方がいれば歓迎です。ご連絡いただければ Discord への招待をお送りします。）

## インストール
[「ladybug_vectorworks」=>「etc」 フォルダ](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/tree/main/ladybug_vectorworks/etc)から　**Install_Ladybugtools_windows_v2022/2018.vwx**　もしくは　**Install_Ladybugtools_mac_v2022/2018.vwx** 個別にダウンロードし、ファイルを開いて記入内容にそってインストールしてください。

インストール後の「ladybug_vectorworks」=>「etc」フォルダ内にはノード一覧(Node_list.vwx)、サンプルファイル(Ladybug-sample.vwx)等が同梱されています。

管理者の環境により、Vectorworks2022でファイルを作成・動作テストを行っております。（vw2018も書き出していますが、動作テストは行っていません。）

また、[こちら](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/releases) より更新履歴を確認できます。

※検証のサンプル数が少ないため、エラー等が残っているところもあるかと思います。エラー等発見しましたら、可能な範囲で対応いたしますので、Disscussionの方で報告いただけるとありがたいです。（皆様と一緒にブラッシュアップしていければ）

※**インストールは自己責任にてお願いいたします**。（仕事環境とは別のPCにてテストしてみることを推奨します。）

※Dragonfly,Butterflyの移植は未定です。要望や協力者の有無により判断したいと思いますので、引き続きご意見や協力していただける方を募集します。

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
Download **Install_Ladybugtools_windows_v2022/2018.vwx** or **Install_Ladybugtools_mac_v2022/2018.vwx** individually from the ["ladybug_vectorworks" => "etc" folder](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/tree/main/ladybug_vectorworks/etc), open the file and follow the instructions to install.

After installation, "ladybug_vectorworks" => "etc" folder contains node list (Node_list.vwx) and sample file (Ladybug-sample.vwx) .

We are creating and testing files with Vectorworks2022 in the administrator's environment. (I have also written vw2018, but I have not tested it.)

You can also check the update history [here](https://github.com/onokennote/Ladybug-tool_for_Vectorworks/releases).

*Since the number of samples for verification is small, there may be some errors. If you find an error, we will respond as much as possible, so we would appreciate it if you could report it in the Discussion. (If you can brush up with everyone)

***install at your own risk**. (It is recommended to test on a PC different from the work environment.)

*The porting of Dragonfly and Butterfly is undecided. We would like to make a decision based on requests and the presence or absence of collaborators, so we are looking for people who can continue to provide opinions and cooperate.

### Ladybug tools (source)
Ladybug Tools 🐞 is a collection of free computer applications that support green design and simulation.

→ladybug tools : https://www.ladybug.tools/index.html
→ladybug tools(github) : https://github.com/ladybug-tools
