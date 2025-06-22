import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
import pandas as pd

class VideoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_youtube_search(self, query, max_results=10):
        """Scrape YouTube search results"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            response = self.session.get(search_url)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            videos = []
            
            # Find script tags containing video data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'var ytInitialData' in script.string:
                    try:
                        # Extract JSON data
                        json_text = script.string
                        start = json_text.find('{')
                        end = json_text.rfind('}') + 1
                        data = json.loads(json_text[start:end])
                        
                        # Navigate through YouTube's data structure
                        contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                        
                        for content in contents:
                            if 'itemSectionRenderer' in content:
                                items = content['itemSectionRenderer'].get('contents', [])
                                for item in items:
                                    if 'videoRenderer' in item:
                                        video = item['videoRenderer']
                                        title = video.get('title', {}).get('runs', [{}])[0].get('text', 'No Title')
                                        video_id = video.get('videoId', '')
                                        thumbnail = video.get('thumbnail', {}).get('thumbnails', [{}])[-1].get('url', '')
                                        duration = video.get('lengthText', {}).get('simpleText', 'Unknown')
                                        views = video.get('viewCountText', {}).get('simpleText', 'Unknown')
                                        
                                        if video_id and len(videos) < max_results:
                                            videos.append({
                                                'platform': 'YouTube',
                                                'title': title,
                                                'url': f'https://www.youtube.com/watch?v={video_id}',
                                                'thumbnail': thumbnail,
                                                'duration': duration,
                                                'views': views,
                                                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                            })
                        break
                    except:
                        continue
            
            return videos[:max_results]
        except Exception as e:
            st.error(f"Error scraping YouTube: {str(e)}")
            return []
    
    def scrape_vimeo_search(self, query, max_results=10):
        """Scrape Vimeo search results"""
        try:
            search_url = f"https://vimeo.com/search?q={urllib.parse.quote(query)}"
            response = self.session.get(search_url)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            videos = []
            
            # Find video elements
            video_elements = soup.find_all('div', class_=re.compile('search_result'))
            
            for element in video_elements[:max_results]:
                try:
                    title_elem = element.find('a', class_=re.compile('link'))
                    if title_elem:
                        title = title_elem.get('title', 'No Title')
                        url = urljoin('https://vimeo.com', title_elem.get('href', ''))
                        
                        # Get thumbnail
                        img_elem = element.find('img')
                        thumbnail = img_elem.get('src', '') if img_elem else ''
                        
                        # Get duration if available
                        duration_elem = element.find('span', class_=re.compile('duration'))
                        duration = duration_elem.text.strip() if duration_elem else 'Unknown'
                        
                        videos.append({
                            'platform': 'Vimeo',
                            'title': title,
                            'url': url,
                            'thumbnail': thumbnail,
                            'duration': duration,
                            'views': 'N/A',
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except:
                    continue
            
            return videos
        except Exception as e:
            st.error(f"Error scraping Vimeo: {str(e)}")
            return []
    
    def scrape_dailymotion_search(self, query, max_results=10):
        """Scrape Dailymotion search results"""
        try:
            search_url = f"https://www.dailymotion.com/search/{urllib.parse.quote(query)}"
            response = self.session.get(search_url)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            videos = []
            
            # Find video containers
            video_containers = soup.find_all('div', {'data-testid': 'video-card'})
            
            for container in video_containers[:max_results]:
                try:
                    # Get title and URL
                    link_elem = container.find('a', href=True)
                    if link_elem:
                        title = link_elem.get('title', 'No Title')
                        url = urljoin('https://www.dailymotion.com', link_elem.get('href', ''))
                        
                        # Get thumbnail
                        img_elem = container.find('img')
                        thumbnail = img_elem.get('src', '') if img_elem else ''
                        
                        # Get duration
                        duration_elem = container.find('span', class_=re.compile('duration'))
                        duration = duration_elem.text.strip() if duration_elem else 'Unknown'
                        
                        videos.append({
                            'platform': 'Dailymotion',
                            'title': title,
                            'url': url,
                            'thumbnail': thumbnail,
                            'duration': duration,
                            'views': 'N/A',
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                except:
                    continue
            
            return videos
        except Exception as e:
            st.error(f"Error scraping Dailymotion: {str(e)}")
            return []
    
    def scrape_all_platforms(self, query, max_per_platform=5):
        """Scrape videos from all platforms"""
        all_videos = []
        platforms = [
            ('YouTube', self.scrape_youtube_search),
            ('Vimeo', self.scrape_vimeo_search),
            ('Dailymotion', self.scrape_dailymotion_search)
        ]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (platform_name, scrape_func) in enumerate(platforms):
            status_text.text(f'Scraping {platform_name}...')
            try:
                videos = scrape_func(query, max_per_platform)
                all_videos.extend(videos)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                st.warning(f"Failed to scrape {platform_name}: {str(e)}")
            
            progress_bar.progress((i + 1) / len(platforms))
        
        status_text.text('Scraping completed!')
        return all_videos

def main():
    st.set_page_config(
        page_title="Video Scraper Tool",
        page_icon="🎥",
        layout="wide"
    )
    
    st.title("🎥 Multi-Platform Video Scraper")
    st.markdown("Search and scrape videos from YouTube, Vimeo, and Dailymotion")
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        max_results_per_platform = st.slider("Max results per platform", 1, 20, 5)
        
        st.header("📋 Platforms")
        st.info("""
        **Supported Platforms:**
        - YouTube
        - Vimeo  
        - Dailymotion
        """)
        
        st.header("⚠️ Disclaimer")
        st.warning("""
        This tool is for educational purposes only. 
        Please respect website terms of service and 
        implement appropriate rate limiting.
        """)
    
    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("🔍 Enter your search query:", placeholder="Enter video search terms...")
    
    with col2:
        st.write("")  # Spacing
        search_button = st.button("🚀 Search Videos", type="primary")
    
    if search_button and query:
        if len(query.strip()) < 2:
            st.error("Please enter a search query with at least 2 characters.")
            return
        
        with st.spinner("Scraping videos from multiple platforms..."):
            scraper = VideoScraper()
            videos = scraper.scrape_all_platforms(query, max_results_per_platform)
        
        if videos:
            st.success(f"Found {len(videos)} videos across platforms!")
            
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Videos", len(videos))
            
            with col2:
                youtube_count = len([v for v in videos if v['platform'] == 'YouTube'])
                st.metric("YouTube", youtube_count)
            
            with col3:
                vimeo_count = len([v for v in videos if v['platform'] == 'Vimeo'])
                st.metric("Vimeo", vimeo_count)
            
            with col4:
                dailymotion_count = len([v for v in videos if v['platform'] == 'Dailymotion'])
                st.metric("Dailymotion", dailymotion_count)
            
            # Filter by platform
            st.subheader("🎬 Video Results")
            
            platform_filter = st.selectbox(
                "Filter by platform:",
                ["All Platforms"] + list(set([v['platform'] for v in videos]))
            )
            
            filtered_videos = videos
            if platform_filter != "All Platforms":
                filtered_videos = [v for v in videos if v['platform'] == platform_filter]
            
            # Display videos in cards
            for i, video in enumerate(filtered_videos):
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if video['thumbnail']:
                            try:
                                st.image(video['thumbnail'], width=200)
                            except:
                                st.write("🎥 No thumbnail")
                        else:
                            st.write("🎥 No thumbnail")
                    
                    with col2:
                        st.subheader(video['title'])
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.write(f"**Platform:** {video['platform']}")
                        with col_b:
                            st.write(f"**Duration:** {video['duration']}")
                        with col_c:
                            st.write(f"**Views:** {video['views']}")
                        
                        st.write(f"**URL:** [Watch Video]({video['url']})")
                        st.write(f"**Scraped:** {video['scraped_at']}")
                
                st.divider()
            
            # Download results
            if st.button("📥 Download Results as CSV"):
                df = pd.DataFrame(filtered_videos)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"video_search_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        else:
            st.warning("No videos found. Try a different search query or check your internet connection.")
    
    elif search_button and not query:
        st.error("Please enter a search query first.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ using Streamlit | "
        "⚠️ Use responsibly and respect website terms of service"
    )

if __name__ == "__main__":
    main()
