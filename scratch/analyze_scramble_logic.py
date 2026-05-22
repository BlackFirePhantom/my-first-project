"""
分析 pctheme.js 中的混淆段落打乱逻辑 (第220行)
该段注释掉的 eval(...) 代码虽然被 // 注释了，但通过解码已知其功能。
我们分析解码后的逻辑来理解它如何打乱段落。
"""

# 解码后的 JS 逻辑（已从 eval(function(p,a,c,k,e,r){...}) 手动解码）：
DECODED_JS = """
document.addEventListener('DOMContentLoaded', function() {
    var container = document.querySelector('#TextContent');
    var originalParagraphs = Array.from(container.querySelectorAll('p'));
    var hiddenClassNames = new Set();
    var date = new Date();
    var hour = date.getHours();
    var minute = date.getMinutes();

    function getRandomLetter() {
        return String.fromCharCode(97 + Math.floor(Math.random() * 26));
    }

    // 给每个原始 p 添加一个随机类名（基于时间+索引+随机数）
    originalParagraphs.forEach(function(paragraph, index) {
        var originalLetter = getRandomLetter();
        var originalRandomPart = Math.random().toString(36).substr(2, 5);
        var originalClassName = originalLetter + hour + minute + index + originalRandomPart;
        paragraph.classList.add(originalClassName);
    });

    // 克隆每个 p，给克隆体也添加随机类名，并将克隆类名存入 hiddenClassNames Set
    var clonedParagraphs = originalParagraphs.map(function(paragraph, index) {
        var clone = paragraph.cloneNode(true);
        var cloneLetter = getRandomLetter();
        var cloneRandomPart = Math.random().toString(36).substr(2, 5);
        var cloneClassName = cloneLetter + hour + minute + index + cloneRandomPart;
        clone.className = cloneClassName;
        hiddenClassNames.add(cloneClassName);
        return clone;
    });

    // 克隆段落打乱顺序
    clonedParagraphs.sort(function() { return Math.random() - 0.5; });

    // 将打乱的克隆段落随机插入到原始段落中间
    clonedParagraphs.forEach(function(clone) {
        var randomIndex = Math.floor(Math.random() * originalParagraphs.length);
        var referenceParagraph = originalParagraphs[randomIndex];
        referenceParagraph.parentNode.insertBefore(clone, referenceParagraph);
    });

    // 创建一个 <style> 标签，把所有克隆段落的类名设为 display: none
    var styleElement = document.createElement('style');
    document.head.appendChild(styleElement);
    var cssRule = Array.from(hiddenClassNames).map(function(k) {
        return "#TextContent ." + k;
    }).join(", ") + " { display: none; }";
    styleElement.sheet.insertRule(cssRule, 0);
});
"""

print("=" * 70)
print("解码后的 JS 混淆逻辑分析")
print("=" * 70)

print("""
【核心机制分析】

1. 【原始段落标记】
   - 给 #TextContent 中每个 <p> 添加一个随机类名（格式：随机字母 + 当前小时 + 当前分钟 + 段落索引 + 随机字符串）
   - 例如：class="a14350abc12"

2. 【克隆段落生成】
   - 对每个原始 <p> 做 cloneNode(true) 克隆
   - 给克隆体设置一个"独立的"随机类名（类似格式）
   - 将克隆类名存入 hiddenClassNames Set

3. 【打乱插入】
   - 克隆段落列表随机洗牌（sort with Math.random()-0.5）
   - 打乱后的克隆段落被随机插入到 DOM 中原始段落旁边

4. 【CSS 隐藏】
   - 动态创建 <style> 标签，注入 CSS 规则：
     #TextContent .克隆类名1, #TextContent .克隆类名2, ... { display: none; }
   - 克隆段落在视觉上被隐藏，原始段落保持可见

5. 【最终状态】
   - DOM 中有 2×N 个 <p> 标签：N 个原始 + N 个克隆（隐藏）
   - 原始段落：有两个类名（随机类名 + 原本可能没有的类名）
   - 克隆段落：只有克隆类名，通过动态 CSS 被隐藏

【关键结论】

★ 不需要登录才能看到内容！
  - 服务器在浏览器中返回完整的 115 个段落（已确认）
  - 混淆是纯客户端 JS 行为：打乱是在浏览器端发生的
  - 只要浏览器执行了这段 JS，就会有正确显示

★ 为什么 Playwright 抓到的 HTML 是混乱的？
  - Playwright 执行了 JS → DOM 变成 2×115=230 个 p 标签
  - 但动态生成的 <style> 注入的 CSS 规则在 page.content() 中
    不会被序列化到 HTML（insertRule 不会修改 <style> 标签的 innerHTML）
  - 所以 page.content() 得到的 HTML：
    * 看到 230 个 p（原始 + 克隆混杂）
    * 但 CSS 隐藏规则不在 HTML 里
  - BeautifulSoup 解析时无法区分哪些是原始段落、哪些是克隆段落

【解决方案】

方案 A（推荐）：用 Playwright 执行 JS 读取 innerText
  - 调用 page.evaluate("document.querySelector('#TextContent').innerText")
  - 浏览器渲染引擎已经正确应用了 CSS，innerText 只返回可见文字

方案 B：在 Playwright 中识别哪些 p 的 CSS display != none
  - page.evaluate 枚举所有 p，用 getComputedStyle 过滤 display:none 的

方案 C：requests 直接抓（不完整，只有16段，不推荐）
""")

print("=" * 70)
print("结论：不需要登录！需要修改 get_content() 的 DOM 提取策略")
print("=" * 70)
