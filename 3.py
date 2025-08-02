import json
import pandas as pd
import os
import re

def fix_json_trailing_commas(json_string):
    """修復 JSON 中的尾隨逗號問題"""
    # 移除物件中最後一個屬性後的逗號
    json_string = re.sub(r',(\s*})', r'\1', json_string)
    # 移除陣列中最後一個元素後的逗號
    json_string = re.sub(r',(\s*])', r'\1', json_string)
    return json_string

def advanced_json_fix(json_string):
    """進階 JSON 修復功能"""
    # 移除多餘的空白和換行
    lines = json_string.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('//'):  # 移除空行和註釋
            cleaned_lines.append(stripped)
    
    # 重新組合
    content = ' '.join(cleaned_lines)
    
    # 修復尾隨逗號
    content = fix_json_trailing_commas(content)
    
    # 確保正確關閉
    open_braces = content.count('{')
    close_braces = content.count('}')
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    
    # 添加缺失的括號
    if open_braces > close_braces:
        content += '}' * (open_braces - close_braces)
    if open_brackets > close_brackets:
        content += ']' * (open_brackets - close_brackets)
    
    return content

def extract_news_data(json_data):
    """
    从JSON数据中提取新闻ID、标题和摘要
    """
    try:
        # 清理並解析JSON数据
        json_data = json_data.strip()
        
        # 使用進階修復功能
        json_data = advanced_json_fix(json_data)
        
        data = json.loads(json_data)
        print(f"✅ JSON 解析成功，頂級鍵: {list(data.keys())}")
        
        news_list = []
        
        # 检查JSON结构
        if 'items' in data and 'data' in data['items']:
            news_items = data['items']['data']
            print(f"📰 找到 {len(news_items)} 條新聞項目")
            
            # 遍历每条新闻
            for idx, item in enumerate(news_items, 1):
                print(f"🔍 處理第 {idx} 條新聞...")
                
                # 檢查必要欄位
                required_fields = ['newsId', 'title', 'summary']
                missing_fields = [field for field in required_fields if field not in item]
                
                if not missing_fields:
                    news_info = {
                        'newsId': str(item['newsId']),
                        'title': item['title'].strip(),
                        'summary': item['summary'].strip(),
                        'publishAt': item.get('publishAt', ''),
                        'categoryName': item.get('categoryName', '未分類'),
                        'link': f"https://news.cnyes.com/news/id/{item['newsId']}"
                    }
                    news_list.append(news_info)
                    print(f"✅ 成功提取: {item['title'][:50]}...")
                else:
                    print(f"❌ 第 {idx} 條新聞缺少欄位: {missing_fields}")
                    print(f"   可用欄位: {list(item.keys())}")
        else:
            print(f"❌ JSON結構不符合預期")
            print(f"   頂級鍵: {list(data.keys())}")
            
            # 嘗試其他可能的結構
            if 'data' in data and isinstance(data['data'], list):
                print("🔄 嘗試直接從 'data' 陣列提取...")
                for item in data['data']:
                    if all(field in item for field in ['newsId', 'title', 'summary']):
                        news_info = {
                            'newsId': str(item['newsId']),
                            'title': item['title'].strip(),
                            'summary': item['summary'].strip(),
                            'publishAt': item.get('publishAt', ''),
                            'categoryName': item.get('categoryName', '未分類'),
                            'link': f"https://news.cnyes.com/news/id/{item['newsId']}"
                        }
                        news_list.append(news_info)
        
        return news_list
    
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {str(e)}")
        print(f"   錯誤位置: 行 {getattr(e, 'lineno', '未知')}, 列 {getattr(e, 'colno', '未知')}")
        
        # 嘗試截取到錯誤位置前的有效部分
        try:
            error_pos = getattr(e, 'pos', 0)
            if error_pos > 100:  # 如果有足夠的內容
                # 嘗試找到最後一個完整的對象
                truncated = json_data[:error_pos-10]  # 稍微往前一點
                
                # 找到最後一個完整的 }
                last_brace = truncated.rfind('}')
                if last_brace > 0:
                    truncated = truncated[:last_brace+1]
                    print("🔄 嘗試使用截取的部分...")
                    try:
                        data = json.loads(truncated)
                        print("✅ 截取部分解析成功！")
                        # 重新處理截取的數據
                        return extract_news_data(truncated)
                    except:
                        pass
        except:
            pass
            
        return []
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        import traceback
        traceback.print_exc()
        return []

def read_json_file(file_path):
    """从文件读取JSON数据"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ 文件 {file_path} 不存在")
            return ""
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"✅ 成功讀取檔案，長度: {len(content)} 字符")
            return content
    except Exception as e:
        print(f"❌ 读取文件错误: {e}")
        return ""

def validate_and_fix_json(file_path):
    """驗證並嘗試修復 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print("🔧 嘗試修復 JSON 文件...")
        
        # 使用進階修復功能
        fixed_content = advanced_json_fix(content)
        
        # 嘗試解析修復後的內容
        try:
            json.loads(fixed_content)
            print(f"✅ 成功修復 JSON 格式")
            
            # 保存修復後的文件
            backup_file = file_path + '.backup'
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"📋 原文件備份為: {backup_file}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"💾 已保存修復後的文件")
            
            return True
        except json.JSONDecodeError as e:
            print(f"❌ 標準修復失敗: {e}")
            
            # 嘗試截取修復
            error_pos = getattr(e, 'pos', len(fixed_content))
            if error_pos > 100:
                print("🔄 嘗試截取修復...")
                # 找到錯誤位置前的最後一個完整結構
                truncated = fixed_content[:error_pos-10]
                last_brace = truncated.rfind('}')
                
                if last_brace > 0:
                    truncated = truncated[:last_brace+1]
                    try:
                        json.loads(truncated)
                        print("✅ 截取修復成功")
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(truncated)
                        return True
                    except:
                        pass
            
            return False
        
    except Exception as e:
        print(f"❌ 修復過程出錯: {e}")
        return False

def main():
    print("=== 鉅亨網新聞資料提取工具 ===\n")
    
    # 检查并尝试修复JSON文件
    if os.path.exists('paste.txt'):
        # 先嘗試讀取原文件
        json_data = read_json_file('paste.txt')
        
        if json_data:
            try:
                # 先嘗試進階修復
                cleaned_data = advanced_json_fix(json_data.strip())
                json.loads(cleaned_data)
                json_data = cleaned_data
                print("✅ 成功修復 JSON 格式問題")
            except json.JSONDecodeError:
                print("🔧 檢測到 JSON 格式問題，嘗試完整修復...")
                if validate_and_fix_json('paste.txt'):
                    # 重新讀取修復後的文件
                    json_data = read_json_file('paste.txt')
                else:
                    print("❌ 標準修復失敗，嘗試強制提取...")
                    # 最後嘗試：直接提取可能的數據
                    json_data = json_data.strip()
    else:
        print("❌ 找不到 paste.txt 文件")
        return
    
    if json_data:
        # 提取新闻数据
        news_list = extract_news_data(json_data)
        
        if news_list:
            print(f"\n🎉 成功提取 {len(news_list)} 條新聞:")
            print("=" * 80)
            
            for i, news in enumerate(news_list, 1):
                print(f"\n📰 新聞 {i}:")
                print(f"   📋 ID: {news['newsId']}")
                print(f"   📝 標題: {news['title']}")
                print(f"   📄 摘要: {news['summary'][:100]}{'...' if len(news['summary']) > 100 else ''}")
                print(f"   🏷️  分類: {news['categoryName']}")
                print(f"   🔗 連結: {news['link']}")
                
            # 保存到CSV文件
            df = pd.DataFrame(news_list)
            output_file = 'cnyes_news_extract.csv'
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ 資料已保存到 {output_file}")
            
            # 顯示CSV檔案資訊
            print(f"📊 CSV檔案包含 {len(df)} 筆記錄，{len(df.columns)} 個欄位")
            print(f"📂 欄位名稱: {', '.join(df.columns)}")
            
        else:
            print("❌ 沒有提取到任何新聞資料")
    else:
        print("❌ 無法讀取資料")

if __name__ == "__main__":
    main()

[
    {
        "type": "command",
        "details": {
            "key": "python.execInTerminal"
        }
    }
]
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