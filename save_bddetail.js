async function savePages() {
    function saveHTML(filename = 'page.html') {
        const html = document.documentElement.outerHTML;
        const blob = new Blob([html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename; // 使用传入的文件名
        document.body.appendChild(a); // 必须将链接添加到DOM中
        a.click(); // 触发下载
        document.body.removeChild(a); // 下载后移除链接
        URL.revokeObjectURL(url);
    }

    var url = window.location.href;
    var match = url.match(/code\/(\d+)/);
    var code = match ? match[1] : 'unknown';
    var clickCount = 0;
    var maxClicks = 4;

    while (clickCount < maxClicks) {
        // 获取当前页码
        var currentPageElement = document.querySelector('.m-pager .cur');
        var cur_pagenum = 0;
        if (currentPageElement) {
            cur_pagenum = currentPageElement.getAttribute('page') || currentPageElement.textContent.trim();
        }

        // 保存当前页面
        saveHTML(`bd_${code}_${cur_pagenum}.html`);

        // 查找“下一页”链接
        var nextPageLink = Array.from(document.querySelectorAll('#m-page a.changePage')).find(function(el) {
            return el.textContent.trim() === '下一页';
        });

        if (nextPageLink) {
            nextPageLink.click();
            clickCount++;

            // 等待10秒，确保页面更新
            await new Promise(resolve => setTimeout(resolve, 10000));

            // 等待后获取新的页码
            var newPageElement = document.querySelector('.m-pager .cur');
            var new_pagenum = 0;
            if (newPageElement) {
                new_pagenum = newPageElement.getAttribute('page') || newPageElement.textContent.trim();
            }

            if (new_pagenum != cur_pagenum) {
                // 页码已更新，保存新页面
                saveHTML(`bd_${code}_${new_pagenum}.html`);
            } else {
                console.log('页面未更新，可能已经是最后一页。');
                break; // 如果页码未变化，退出循环
            }
        } else {
            console.log('未找到“下一页”链接，可能已经是最后一页。');
            break; // 退出循环
        }
    }
}

// 启动函数
savePages();
