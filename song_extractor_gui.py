import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import gequbao as m
import time

class SongExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("歌曲提取工具")
        self.root.geometry("800x600")
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建输入区域
        self.input_frame = ttk.LabelFrame(self.main_frame, text="歌曲输入，格式为：歌名 - 歌手，每行一首歌", padding="10")
        self.input_frame.pack(fill=tk.X, pady=5)
        
        # 创建文本输入框，至少8行
        self.input_text = scrolledtext.ScrolledText(self.input_frame, height=10, width=80)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮区域
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=5)
        
        # 提取按钮
        self.extract_button = ttk.Button(self.button_frame, text="提取歌曲", command=self.start_extraction)
        self.extract_button.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        self.clear_button = ttk.Button(self.button_frame, text="清空输入", command=self.clear_input)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # 保存歌单按钮
        self.save_button = ttk.Button(self.button_frame, text="保存歌单", command=self.save_playlist, state=tk.DISABLED)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        # 创建结果区域
        self.result_frame = ttk.LabelFrame(self.main_frame, text="提取结果", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建结果列表
        self.result_tree = ttk.Treeview(self.result_frame, columns=("name", "singer", "link"), show="headings")
        self.result_tree.heading("name", text="歌名")
        self.result_tree.heading("singer", text="歌手")
        self.result_tree.heading("link", text="链接")
        
        # 设置列宽
        self.result_tree.column("name", width=200)
        self.result_tree.column("singer", width=200)
        self.result_tree.column("link", width=400)
        
        # 添加滚动条
        self.scrollbar = ttk.Scrollbar(self.result_frame, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        
        # 创建状态区域
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=5)
        
        # 状态标签
        self.status_label = ttk.Label(self.status_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(self.status_frame, mode="determinate")
        self.progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=10)
        
        # 歌单列表
        self.playlist = []
    
    def clear_input(self):
        """清空输入框"""
        self.input_text.delete(1.0, tk.END)
    
    def start_extraction(self):
        """开始提取歌曲"""
        # 清空结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.playlist = []
        
        # 获取输入内容
        input_content = self.input_text.get(1.0, tk.END).strip()
        if not input_content:
            messagebox.showwarning("警告", "请输入歌曲信息")
            return
        
        # 解析输入内容
        songs = input_content.split('\n')
        songs = [song.strip() for song in songs if song.strip()]
        
        if not songs:
            messagebox.showwarning("警告", "请输入有效的歌曲信息")
            return
        
        # 设置进度条
        self.progress["maximum"] = len(songs)
        self.progress["value"] = 0
        
        # 单线程处理每个歌曲
        processed = 0
        total = len(songs)
        
        for song_input in songs:
            # 处理单个歌曲
            self.process_song(song_input)
            # 更新进度
            processed += 1
            self.progress["value"] = processed
            self.status_label.config(text=f"已处理 {processed}/{total}")
            # 强制更新UI
            self.root.update_idletasks()
        
        # 所有任务完成
        self.status_label.config(text="提取完成")
        self.save_button.config(state=tk.NORMAL)
    

    
    def process_song(self, song_input):
        """处理单个歌曲"""
        try:
            # 解析歌名和歌手
            if " - " in song_input:
                name, singer = song_input.split(" - ", 1)
                name = name.strip()
                singer = singer.strip()
            else:
                messagebox.showerror("错误", f"处理 {song_input} 时出错: 输入格式错误，请使用 '歌名 - 歌手' 格式")
                return
            
            # 搜索歌曲，添加重试机制
            max_retries = 3
            retry_count = 0
            search_results = []
            
            while retry_count < max_retries:
                # 更新状态
                self.status_label.config(text=f"正在搜索: {name} - {singer} (尝试 {retry_count+1}/{max_retries})")
                self.root.update_idletasks()
                
                search_results = m.request_list(f'{name} - {singer}')
                
                if search_results:
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = 2 * retry_count  # 指数退避
                        self.status_label.config(text=f"搜索结果为空，{wait_time}秒后重试...")
                        self.root.update_idletasks()
                        time.sleep(wait_time)
            
            if not search_results:
                messagebox.showerror("错误", f"处理 {song_input} 时出错: 未找到搜索结果")
                return
            
            # 处理搜索结果
            self.status_label.config(text=f"找到 {len(search_results)} 个结果")
            self.root.update_idletasks()
            
            # 尝试匹配
            matched_song = None
            for song in search_results:
                # 处理歌手名称格式差异
                song_singer = song['singer'].replace('&', '、')
                if song['name'] == name and song_singer == singer:
                    matched_song = song
                    break
            
            if matched_song:
                # 成功匹配
                self.playlist.append(matched_song)
                self.result_tree.insert("", tk.END, values=(matched_song['name'], matched_song['singer'], matched_song['link']))
                self.root.update_idletasks()
            else:
                # 显示选择对话框
                self.show_selection_dialog(name, singer, search_results)
        except Exception as e:
            messagebox.showerror("错误", f"处理 {song_input} 时出错: {str(e)}")
    

    
    def show_selection_dialog(self, name, singer, search_results):
        """显示选择对话框"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(f"选择歌曲: {name} - {singer}")
        dialog.geometry("600x400")
        
        # 创建列表框
        listbox = tk.Listbox(dialog, width=80, height=15)
        listbox.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # 添加搜索结果
        for i, song in enumerate(search_results):
            listbox.insert(tk.END, f"{i+1}. {song['name']} - {song['singer']}")
        
        # 创建按钮区域
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 选择结果变量
        self.selected_song = None
        
        def on_select():
            try:
                selection = listbox.curselection()
                if selection:
                    index = selection[0]
                    self.selected_song = search_results[index]
                    dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"选择出错: {str(e)}")
        
        def on_cancel():
            self.selected_song = None
            dialog.destroy()
        
        # 选择按钮
        select_button = ttk.Button(button_frame, text="选择", command=on_select)
        select_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # 等待对话框关闭
        dialog.wait_window()
        
        # 如果用户选择了歌曲，添加到歌单
        if self.selected_song:
            self.playlist.append(self.selected_song)
            self.result_tree.insert("", tk.END, values=(self.selected_song['name'], self.selected_song['singer'], self.selected_song['link']))
    
    def save_playlist(self):
        """保存歌单"""
        if not self.playlist:
            messagebox.showwarning("警告", "歌单为空，无需保存")
            return
        
        # 保存为文本文件
        try:
            with open("playlist.txt", "w", encoding="utf-8") as f:
                for song in self.playlist:
                    f.write(f"{song['name']} - {song['singer']} - {song['link']}\n")
            messagebox.showinfo("成功", "歌单已保存到 playlist.txt")
        except Exception as e:
            messagebox.showerror("错误", f"保存歌单失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SongExtractorGUI(root)
    root.mainloop()