import requests
import pandas as pd
import datetime as dt
import json
import time

def scrape_cnyes_news(days=10, page_limit=None):
    """
    專業的鉅亨網新聞爬蟲
    
    Args:
        days: 爬取過去幾天的新聞 (預設10天)
        page_limit: 限制頁數 (None = 爬取所有頁面)
    """
    print("🚀 開始爬取鉅亨網新聞...")
    
    data = []
    url = "https://api.cnyes.com/media/api/v1/newslist/category/headline"
    
    # 設定時間範圍
    end_time = dt.datetime.today()
    start_time = end_time - dt.timedelta(days=days)
    
    payload = {
        "page": 1,
        "limit": 30,
        "isCategoryHeadline": 1,
        "startAt": int(start_time.timestamp()),
        "endAt": int(end_time.timestamp())
    }
    
    try:
        # 第一次請求以獲取總頁數
        print(f"📡 發送請求到 API...")
        response = requests.get(url, params=payload, timeout=10)
        response.raise_for_status()
        
        jd = json.loads(response.text)
        total_pages = jd['items']['last_page']
        
        print(f"📄 總共 {total_pages} 頁資料")
        
        # 處理第一頁
        data.append(pd.DataFrame(jd['items']['data']))
        print(f"✅ 第 1 頁完成 ({len(jd['items']['data'])} 條新聞)")
        
        # 處理後續頁面
        max_pages = min(total_pages, page_limit) if page_limit else total_pages
        
        for i in range(2, max_pages + 1):
            print(f"📡 處理第 {i}/{max_pages} 頁...")
            
            payload["page"] = i
            response = requests.get(url, params=payload, timeout=10)
            response.raise_for_status()
            
            jd = json.loads(response.text)
            data.append(pd.DataFrame(jd['items']['data']))
            
            print(f"✅ 第 {i} 頁完成 ({len(jd['items']['data'])} 條新聞)")
            
            # 添加延遲避免過於頻繁的請求
            time.sleep(0.5)
        
        # 合併資料
        df = pd.concat(data, ignore_index=True)
        
        # 處理資料
        df = df[['newsId', 'title', 'summary']]
        df['link'] = df['newsId'].apply(lambda x: f'https://m.cnyes.com/news/id/{x}')
        
        # 儲存到 CSV
        output_file = 'news.csv'
        df.to_csv(output_file, encoding='utf-8-sig', index=False)
        
        print(f"\n🎉 爬取完成！")
        print(f"📊 總共爬取 {len(df)} 條新聞")
        print(f"💾 已儲存到 {output_file}")
        
        # 顯示範例
        print(f"\n📰 新聞範例 (前3條):")
        for i, row in df.head(3).iterrows():
            print(f"  {i+1}. {row['title'][:60]}...")
        
        return df
        
    except requests.RequestException as e:
        print(f"❌ HTTP 請求錯誤: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {e}")
        return None
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return None

if __name__ == "__main__":
    # 執行爬蟲
    df = scrape_cnyes_news(days=10)
    
    if df is not None:
        print(f"\n✅ 成功完成新聞爬取任務！")
    else:
        print(f"\n❌ 爬取失敗，請檢查網路連接和 API 狀態")