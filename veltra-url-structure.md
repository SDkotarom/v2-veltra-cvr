# VELTRA URL構造定義（veltra.com/jp/ 配下）

> **目的**: エリアセグメント分析でのpage_pathフィルタ定義、ダッシュボード表示用のパス参照
> **ソース**: veltra.com/jp カテゴリ構造（2026年4月時点）

---

## リージョン一覧

| リージョン | パス |
|---|---|
| ハワイ | `/jp/hawaii/` |
| オセアニア | `/jp/oceania/` |
| アジア | `/jp/asia/` |
| ビーチリゾート | `/jp/beach_resort/` |
| 日本 | `/jp/japan/` |
| ヨーロッパ | `/jp/europe/` |
| アメリカ・カナダ | `/jp/north_america/` |
| 中南米・カリブ海 | `/jp/latin_america/` |
| 中東 | `/jp/mideast/` |
| アフリカ | `/jp/africa/` |

---

## エリア × セグメントキー マッピング（20セグメント）

data.json の `segments.area` キーと VELTRA URL の対応:

| セグメントキー | 表示名 | VELTRAパス | GA4フィルタ |
|---|---|---|---|
| `hawaii` | ハワイ | `/jp/hawaii/` | `/hawaii/` を含む |
| `bali` | バリ | `/jp/asia/indonesia/bali/` | `/bali/` を含む |
| `guam` | グアム | `/jp/beach_resort/guam/` | `/guam/` を含む |
| `cebu` | セブ | `/jp/asia/philippines/cebu/` | `/cebu/` を含む |
| `singapore` | シンガポール | `/jp/asia/singapore/` | `/singapore/` を含む |
| `taiwan` | 台湾 | `/jp/asia/taiwan/` | `/taiwan/` を含む |
| `hongkong` | 香港・マカオ | `/jp/asia/hongkong/` | `/hongkong/` を含む |
| `thailand` | タイ | `/jp/asia/thailand/` | `/thailand/` を含む |
| `vietnam` | ベトナム | `/jp/asia/vietnam/` | `/vietnam/` を含む |
| `europe` | ヨーロッパ | `/jp/europe/` | `/europe/` を含む |
| `australia` | オーストラリア | `/jp/oceania/australia/` | `/australia/` を含む |
| `okinawa` | 沖縄 | `/jp/japan/okinawa/` | `/okinawa/` を含む |
| `tokyo` | 東京 | `/jp/japan/tokyo/` | `/tokyo/` を含む |
| `osaka` | 大阪 | `/jp/japan/osaka/` | `/osaka/` を含む |
| `kyoto` | 京都 | `/jp/japan/kyoto/` | `/kyoto/` を含む |
| `hokkaido` | 北海道 | `/jp/japan/hokkaido/` | `/hokkaido/` を含む |
| `kanto` | 関東 | `/jp/japan/kanto/` | `/kanto/` を含む |
| `kyushu` | 九州 | `/jp/japan/kyushu/` | `/kyushu/` を含む |
| `ishigaki_miyako` | 石垣島・宮古島 | `/jp/japan/okinawa/ishigaki_yaeyama/` | `/ishigaki/` or `/miyako/` を含む |
| `other` | その他 | — | 上記以外 |

---

## 全エリア詳細URL（リージョン別）

### ハワイ `/jp/hawaii/`
| エリア | パス |
|---|---|
| オアフ島(ホノルル) | `/jp/hawaii/oahu/` |
| ハワイ島 | `/jp/hawaii/big_island/` |
| マウイ島 | `/jp/hawaii/maui/` |
| カウアイ島 | `/jp/hawaii/kauai/` |
| ラナイ島 | `/jp/hawaii/lanai/` |
| モロカイ島 | `/jp/hawaii/molokai/` |

### オセアニア `/jp/oceania/`
| エリア | パス |
|---|---|
| オーストラリア | `/jp/oceania/australia/` |
| ├ ケアンズ | `/jp/oceania/australia/cairns/` |
| ├ シドニー | `/jp/oceania/australia/sydney/` |
| ├ ゴールドコースト | `/jp/oceania/australia/gold_coast/` |
| ├ メルボルン | `/jp/oceania/australia/melbourne/` |
| └ 他多数 | `/jp/oceania/australia/*/` |
| ニュージーランド | `/jp/oceania/new_zealand/` |
| ├ オークランド | `/jp/oceania/new_zealand/auckland/` |
| └ 他多数 | `/jp/oceania/new_zealand/*/` |
| パプアニューギニア | `/jp/oceania/papua_new_guinea/` |
| フィジー | `/jp/beach_resort/fiji/` |

### アジア `/jp/asia/`
| エリア | パス |
|---|---|
| タイ | `/jp/asia/thailand/` |
| ├ バンコク | `/jp/asia/thailand/bangkok/` |
| ├ プーケット | `/jp/asia/thailand/phuket/` |
| └ 他 | `/jp/asia/thailand/*/` |
| 台湾 | `/jp/asia/taiwan/` |
| ├ 台北 | `/jp/asia/taiwan/taipei/` |
| └ 他 | `/jp/asia/taiwan/*/` |
| 韓国 | `/jp/asia/korea/` |
| ベトナム | `/jp/asia/vietnam/` |
| マレーシア | `/jp/asia/malaysia/` |
| フィリピン | `/jp/asia/philippines/` |
| ├ セブ島 | `/jp/asia/philippines/cebu/` |
| └ マニラ | `/jp/asia/philippines/manila/` |
| インドネシア | `/jp/asia/indonesia/` |
| ├ バリ島 | `/jp/asia/indonesia/bali/` |
| └ ジャカルタ | `/jp/asia/indonesia/jakarta/` |
| カンボジア | `/jp/asia/cambodia/` |
| シンガポール | `/jp/asia/singapore/` |
| 香港・マカオ | `/jp/asia/hongkong/` |
| インド | `/jp/asia/india/` |
| スリランカ | `/jp/asia/sri_lanka/` |
| 中国 | `/jp/asia/china/` |

### ビーチリゾート `/jp/beach_resort/`
| エリア | パス |
|---|---|
| グアム | `/jp/beach_resort/guam/` |
| サイパン | `/jp/beach_resort/saipan/` |
| パラオ | `/jp/beach_resort/palau/` |
| モルディブ | `/jp/beach_resort/maldives/` |
| タヒチ | `/jp/beach_resort/tahiti/` |
| ニューカレドニア | `/jp/beach_resort/new_caledonia/` |

### 日本 `/jp/japan/`
| エリア | パス |
|---|---|
| 北海道 | `/jp/japan/hokkaido/` |
| 東北地方 | `/jp/japan/tohoku/` |
| 関東地方 | `/jp/japan/kanto/` |
| 東京 | `/jp/japan/tokyo/` |
| 神奈川 | `/jp/japan/kanagawa/` |
| 千葉 | `/jp/japan/chiba/` |
| 北陸地方 | `/jp/japan/hokuriku/` |
| 甲信越 | `/jp/japan/koshinetsu/` |
| 東海地方 | `/jp/japan/tokai/` |
| 静岡 | `/jp/japan/shizuoka/` |
| 名古屋・愛知 | `/jp/japan/aichi/` |
| 京都 | `/jp/japan/kyoto/` |
| 大阪 | `/jp/japan/osaka/` |
| 兵庫 | `/jp/japan/hyogo/` |
| 奈良 | `/jp/japan/nara/` |
| 和歌山 | `/jp/japan/wakayama/` |
| 山陰・山陽 | `/jp/japan/sanin_sanyo/` |
| 四国 | `/jp/japan/shikoku/` |
| 九州地方 | `/jp/japan/kyushu/` |
| 福岡 | `/jp/japan/fukuoka/` |
| 沖縄 | `/jp/japan/okinawa/` |
| ├ 沖縄本島 | `/jp/japan/okinawa/okinawa_main_island/` |
| ├ 石垣島・八重山 | `/jp/japan/okinawa/ishigaki_yaeyama/` |
| ├ 宮古島 | `/jp/japan/okinawa/miyako_island/` |
| └ 西表島 | `/jp/japan/okinawa/iriomote_island/` |
| 屋久島 | `/jp/japan/yakushima/` |
| 奄美大島 | `/jp/japan/amamioshima/` |

### ヨーロッパ `/jp/europe/`
| エリア | パス |
|---|---|
| イタリア | `/jp/europe/italy/` |
| フランス | `/jp/europe/france/` |
| スペイン | `/jp/europe/spain/` |
| イギリス | `/jp/europe/uk/` |
| ドイツ | `/jp/europe/germany/` |
| オーストリア | `/jp/europe/austria/` |
| トルコ | `/jp/europe/turkey/` |
| スイス | `/jp/europe/switzerland/` |
| フィンランド | `/jp/europe/finland/` |
| アイスランド | `/jp/europe/iceland/` |
| ポルトガル | `/jp/europe/portugal/` |
| ギリシャ | `/jp/europe/greece/` |
| チェコ | `/jp/europe/czech/` |
| ハンガリー | `/jp/europe/hungary/` |
| クロアチア | `/jp/europe/croatia/` |
| ノルウェー | `/jp/europe/norway/` |

### アメリカ・カナダ `/jp/north_america/`
| エリア | パス |
|---|---|
| カナダ | `/jp/north_america/canada/` |
| ニューヨーク | `/jp/north_america/new_york/` |
| ラスベガス | `/jp/north_america/las_vegas/` |
| ロサンゼルス | `/jp/north_america/los_angeles/` |
| サンフランシスコ | `/jp/north_america/san_francisco/` |
| アラスカ | `/jp/north_america/alaska/` |

### 中南米・カリブ海 `/jp/latin_america/`
| エリア | パス |
|---|---|
| メキシコ | `/jp/latin_america/mexico/` |
| ├ カンクン | `/jp/latin_america/mexico/cancun/` |
| ペルー | `/jp/latin_america/peru/` |
| ブラジル | `/jp/latin_america/brazil/` |
| アルゼンチン | `/jp/latin_america/argentina/` |

### 中東 `/jp/mideast/`
| エリア | パス |
|---|---|
| アラブ首長国連邦 | `/jp/mideast/uae/` |
| ├ ドバイ | `/jp/mideast/uae/dubai/` |
| ヨルダン | `/jp/mideast/jordan/` |

### アフリカ `/jp/africa/`
| エリア | パス |
|---|---|
| エジプト | `/jp/africa/egypt/` |
| モロッコ | `/jp/africa/morocco/` |
| 南アフリカ | `/jp/africa/south_africa/` |
| ケニア | `/jp/africa/kenya/` |
| タンザニア | `/jp/africa/tanzania/` |

---

*2026年4月時点 / veltra.com/jp カテゴリ構造*
