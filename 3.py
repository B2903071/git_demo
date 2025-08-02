import requests
import pandas as pd
import datetime as dt
import json
import os

def scrape_cnyes_news():
    """爬取鉅亨網新聞並驗證成功"""
    try:
        print("🚀 開始爬取鉅亨網新聞...")
        
        data = []
        url = "https://api.cnyes.com/media/api/v1/newslist/category/headline"
        payload = {
            "page": 1,
            "limit": 30,
            "isCategoryHeadline": 1,
            "startAt": int((dt.datetime.today() - dt.timedelta(days=10)).timestamp()),
            "endAt": int(dt.datetime.today().timestamp())
        }
        
        # 獲取第一頁
        print("📥 正在獲取第1頁...")
        res = requests.get(url, params=payload, timeout=30)
        res.raise_for_status()  # 檢查HTTP錯誤
        
        jd = json.loads(res.text)
        data.append(pd.DataFrame(jd['items']['data']))
        
        total_pages = jd['items']['last_page']
        print(f"📄 總共發現 {total_pages} 頁")
        
        # 獲取其他頁面
        for i in range(2, total_pages + 1):
            print(f"📥 正在獲取第 {i}/{total_pages} 頁...")
            payload["page"] = i
            
            res = requests.get(url, params=payload, timeout=30)
            res.raise_for_status()
            jd = json.loads(res.text)
            data.append(pd.DataFrame(jd['items']['data']))
        
        # 處理資料
        df = pd.concat(data, ignore_index=True)
        df = df[['newsId', 'title', 'summary']]
        df['link'] = df['newsId'].apply(lambda x: f'https://m.cnyes.com/news/id/{x}')
        
        # 保存檔案
        filename = 'news.csv'
        df.to_csv(filename, encoding='utf-8-sig', index=False)
        
        # 驗證成功
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"✅ 爬取成功!")
            print(f"📊 總共獲取 {len(df)} 筆新聞")
            print(f"💾 檔案已保存: {filename} ({file_size} bytes)")
            print(f"📋 欄位: {', '.join(df.columns)}")
            
            # 顯示範例
            print("\n📰 新聞範例:")
            for i, row in df.head(3).iterrows():
                print(f"  {i+1}. {row['title'][:50]}...")
            
            return True
        else:
            print("❌ 檔案保存失敗")
            return False
            
    except requests.RequestException as e:
        print(f"❌ 網路請求錯誤: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")
        return False

if __name__ == "__main__":
    success = scrape_cnyes_news()
    if success:
        print("🎉 程式執行成功!")
    else:
        print("💥 程式執行失敗!")