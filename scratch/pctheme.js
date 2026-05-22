function Go(a) {
    window.location = a
}
function login() {
    function k(a) {
        var b = a + "=",
        c = "";
        return document.cookie.length > 0 && (offset = document.cookie.indexOf(b), -1 != offset && (offset += b.length, end = document.cookie.indexOf(";", offset), -1 == end && (end = document.cookie.length), c = unescape(document.cookie.substring(offset, end)))),
        c
    }
    var j, a = 0,
    b = "",
    c = "",
    d = 0,
    e = 0,
    f = 0,
    g = "",
    h = "";
    if (document.cookie.indexOf("jieqiUserInfo") >= 0) for (j = k("jieqiUserInfo"), start = 0, offset = j.indexOf(",", start); offset > 0;) tmpval = j.substring(start, offset),
    tmpidx = tmpval.indexOf("="),
    tmpidx > 0 && (tmpname = tmpval.substring(0, tmpidx), tmpval = tmpval.substring(tmpidx + 1, tmpval.length), "jieqiUserId" == tmpname ? a = tmpval: "jieqiUserName_un" == tmpname ? b = tmpval: "jieqiUserPassword" == tmpname ? c = tmpval: "jieqiUserGroup" == tmpname ? d = tmpval: "jieqiNewMessage" == tmpname ? e = tmpval: "jieqiUserVip" == tmpname ? f = tmpval: "jieqiUserHonor_un" == tmpname ? g = tmpval: "jieqiUserGroupName_un" == tmpname && (h = tmpval)),
    start = offset + 1,
    offset < j.length ? (offset = j.indexOf(",", start), -1 == offset && (offset = j.length)) : offset = -1;
    0 == a || "" == b || -1 == document.cookie.indexOf("PHPSESSID") && "" == c ? (document.write('<form action="/login.php"  name="frmlogin" method="post">'), document.write('<div class="unloginl">'), document.write('<input type="text" name="username" placeholder="帐号" class="putk">'), document.write(' <input type="password" name="password" placeholder="密码" class="putk">'), document.write(' <input type="hidden" class="login_box" checked="checked" name="usecookie" value="315360000"> '), document.write(' <input class="loginbtn" type="hidden" name="action" value="login">'), document.write(' <input type="submit" name="submit" class="logint" value="登录">&nbsp;&nbsp;<a href="/register.php">注册</a>'), document.write("</form>")) : (document.write("<b>Hi " + b + ' </b>，<a href="/user">个人中心</a> | <a href="/bookcase">我的书架</a>'), e > 0 ? document.write(' | <a href="/message.php?box=inbox" style="color:#f00">您有短信</a>') : document.write(' | <a href="/message.php?box=inbox">收件箱</a>'), document.write(' | <a href="/logout.php" target="_self">退出</a>'))
}
function sq(a, b, c) {
    e = "/modules/article/addbookcase.php?bid=" + a + "&cid=" + b + "&pid=" + c + "&ajax_request=1",
    $.get(e,
    function(a) {
        alert(a.replace("<br />", "").replace(/(\<br \/\>)/g, "\r\n"))
    })
}
function tjp(a) {
    e = "/modules/article/uservote.php?id=" + a + "&ajax_request=1",
    $.get(e,
    function(a) {
        alert(a.replace("<br />", "").replace(/(\<br \/\>)/g, "\r\n"))
    })
}
function dj(a) {
    $.get("/click?id=" + a)
}

function tj() {

}

function ahToggle() {
  if (localStorage.getItem("禁用章评") === null) {
    localStorage.setItem("禁用章评", "true")
    location.reload()
  } else {
    localStorage.removeItem("禁用章评")
    location.reload()
  }
}
if (localStorage.getItem("禁用章评") === null) {
  var ahBtn = 'class="zt hover">开启</span><span class="zt"'
} else {
  var ahBtn = 'class="zt">开启</span><span class="zt hover"'
}
$(".mlfy_main_sz>ul").append(
  '<li><span class="fl">章评模式</span><span onclick="ahToggle()" ' +
    ahBtn +
    ' onclick="ahToggle()">关闭</span></li>'
)

function shezhi() {
    document.writeln('<div class="container"><ul class="links"><li><a onclick="sq(' + bid + "," + cid + "," + page + ');">标记书签</a> | </li><li><a onclick="tjp(' + bid + ');">给书点赞</a> | </li><li><a href="/newmessage.php?tosys=1&amp;title=' + name + ' 有错误&content=https://www.linovelib.com/modules/article/chapteredit.php?id='+ cid +'%0D%0A请明确错误原因%0D%0A%0D%0A">报错求书</a> | </li><li><a href="/recentread">阅读记录</a></li> | <li><a id="GB_BIG" href="javascript:translatePage();" style="color:#6f90a0">繁體化</a></li></ul>'),
    document.writeln('<div class="mlfy_main_l"><i class="szk"><em class="icon-cog"></em> <z>阅读</z>设置</i><i class="hid">（推荐配合 快捷键[F11] 进入全屏沉浸式阅读）</i></div></div>'),
    document.writeln('<div class="mlfy_main_sz b2" ><p class="ml"><span class="txt">设置</span><span class="close">X</span></p><ul><li><span class="fl">阅读主题</span><i class="c1"></i><i class="c2"></i><i class="c3"></i><i class="c4"></i><i class="c5"></i><i class="c6 hover"></i><i class="c7"></i><i class="c8"></i></li> <li class="hid"><span class="fl">正文字体</span><span class="zt hover">雅黑</span><span class="zt">宋体</span><span class="zt">楷体</span><span class="zt" title="方正启体简体">启体</span><span class="zt" title="思源黑体 CN">思源</span><span class="zt" title="苹方字体">苹方</span></li><li><span class="fl">字体大小</span><span class="dx dxl">A-</span><span class="dx dxc">20</span><span class="dx dxr">A+</span></li><li class="hid"><span class="fl">页面宽度</span><p class="dx kdl"><span class="icon"></span><span class="fl">-</span></p><p class="dx kdc">100%</p><p class="dx kdr"><span class="icon"></span><span class="fl">+</span></p></ul><div class="btn-wrap"><a class="red-btn" href="javascript:">保存</a><a class="grey-btn" href="javascript:">取消</a></div></div>')
}
function yuedu() {
    function a() {
        var a = -parseInt($(".mlfy_main").css("width")) / 2 - 60,
        b = a + 70 + "px";
        $(".mlf11y_main_l").css("margin-left", a + "px"),
        $(".mlfy_main_r").css("margin-right", a + "px"),
        $(".mlfy_main_sz").css("margin-left", b)
    }
    function b() {
        $(".mlfy_main_sz").removeClass("hover"),
        $(".mlfy_main_l i").removeClass("hover")
    }
    function c() {
        var a, b, c;
        void 0 != $.cookie("xszjsz") && (a = $.cookie("xszjsz").split(","), $("body").removeClass().addClass(a[0]), b = a[0].substring(2, 3) - 1, $(".mlfy_main_sz.b2 ul li i").eq(b).addClass("hover").siblings().removeClass("hover"), c = a[1].substring(2, 3) - 1, $(".mlfy_main_sz.b2 ul li .zt").eq(c).addClass("hover").siblings().removeClass("hover"), $("#mlfy_main_text").removeClass().addClass(a[1]), $(".mlfy_main_sz.b2 ul li .dxc").text(a[2]), $("#mlfy_main_text").css("font-size", a[2] + "px"), $(".mlfy_main_sz.b2 ul li .kdc").text(a[3]), $(".bar,.mlfy_main,.mlfy_add,.mlfy_page").css("width", a[3] + "px"), e = $.inArray(a[3], d))
    }
    var d, e, f, g, h, i, j, k;
    tj(),
    !
    function(a) {
        "function" == typeof define && define.amd ? define(["jquery"], a) : a("object" == typeof exports ? require("jquery") : jQuery)
    } (function(a) {
        function b(a) {
            return h.raw ? a: encodeURIComponent(a)
        }
        function c(a) {
            return h.raw ? a: decodeURIComponent(a)
        }
        function d(a) {
            return b(h.json ? JSON.stringify(a) : String(a))
        }
        function e(a) {
            0 === a.indexOf('"') && (a = a.slice(1, -1).replace(/\\"/g, '"').replace(/\\\\/g, "\\"));
            try {
                return a = decodeURIComponent(a.replace(g, " ")),
                h.json ? JSON.parse(a) : a
            } catch(a) {}
        }
        function f(b, c) {
            var d = h.raw ? b: e(b);
            return a.isFunction(c) ? c(d) : d
        }
        var g = /\+/g,
        h = a.cookie = function(e, g, i) {
            var j, k, l, m, n, o, p, q, r;
            if (void 0 !== g && !a.isFunction(g)) return i = a.extend({},
            h.defaults, i),
            "number" == typeof i.expires && (j = i.expires, k = i.expires = new Date, k.setTime( + k + 864e5 * j)),
            document.cookie = [b(e), "=", d(g), i.expires ? "; expires=" + i.expires.toUTCString() : "", i.path ? "; path=" + i.path: "", i.domain ? "; domain=" + i.domain: "", i.secure ? "; secure": ""].join("");
            for (l = e ? void 0 : {},
            m = document.cookie ? document.cookie.split("; ") : [], n = 0, o = m.length; o > n; n++) {
                if (p = m[n].split("="), q = c(p.shift()), r = p.join("="), e && e === q) {
                    l = f(r, g);
                    break
                }
                e || void 0 === (r = f(r)) || (l[q] = r)
            }
            return l
        };
        h.defaults = {},
        a.removeCookie = function(b, c) {
            return void 0 !== a.cookie(b) && (a.cookie(b, "", a.extend({},
            c, {
                expires: -1
            })), !a.cookie(b))
        }
    }),
    d = ["640", "800", "990", "1200", "1400"],
    e = 2,
    void 0 != $.cookie("xszjsz") && (f = $.cookie("xszjsz").split(","), g = $.inArray(f[3], d), e = g),
    c(),
    a(),
    $(".szk").click(function() {
        $(".mlfy_main_sz,.szk").addClass("hover").siblings(".mlfy_main_sz").removeClass("hover")
    }),
    h = ["bg1", "bg2", "bg3", "bg4", "bg5", "bg6", "bg7", "bg8"],
    $(".mlfy_main_sz.b2 ul li i").click(function() {
        $(this).addClass("hover").siblings().removeClass("hover");
        var a = $(this).index() - 1;
        $("body").removeClass().addClass(h[a])
    }),
    i = ["zt1", "zt2", "zt3", "zt4", "zt5", "zt6"],
    $(".mlfy_main_sz.b2 ul li .zt").click(function() {
        $(this).addClass("hover").siblings().removeClass("hover");
        var a = $(this).index() - 1;
        $("#mlfy_main_text").removeClass().addClass(i[a])
    }),
    $(".mlfy_main_sz.b2 ul li .dxl").click(function() {
        var a = parseInt($(".mlfy_main_sz.b2 ul li .dxc").text());
        a > 12 && (a -= 2, $(".mlfy_main_sz.b2 ul li .dxc").text(a), $("#mlfy_main_text").css("font-size", a))
    }),
    $(".mlfy_main_sz.b2 ul li .dxr").click(function() {
        var a = parseInt($(".mlfy_main_sz.b2 ul li .dxc").text());
        48 > a && (a += 2, $(".mlfy_main_sz.b2 ul li .dxc").text(a), $("#mlfy_main_text").css("font-size", a))
    }),
    $(".mlfy_main_sz.b2 ul li .kdl").click(function() {
        e > 0 && (e -= 1, $(".bar,.mlfy_main,.mlfy_add,.mlfy_page").css("width", d[e] + "px"), $(".kdc").text(d[e]), a())
    }),
    $(".mlfy_main_sz>ul").append(
    '<li><span class="fl">章评模式</span><span onclick="ahToggle()" ' +
    ahBtn +
    ' onclick="ahToggle()">关闭</span></li>'
    ),
    $(".mlfy_main_sz.b2 ul li .kdr").click(function() {
        4 > e && (e += 1, $(".bar,.mlfy_main,.mlfy_add,.mlfy_page").css("width", d[e] + "px"), $(".kdc").text(d[e]), a())
    }),
    $(".mlfy_main_sz.b2 ul li .yd").click(function() {
        $(this).addClass("hover").siblings().removeClass("hover")
    }),
    $(".mlfy_main_sz.b2 ul li .zd").click(function() {
        "开启" == $(this).text() ? ($(this).text("关闭").animate({
            left: "0px"
        }), $(this).parent().removeClass("on").addClass("off")) : ($(this).text("开启").animate({
            left: "20px"
        }), $(this).parent().removeClass("off").addClass("on"))
    }),
    $(".mlfy_main_sz.b2 .red-btn").click(function() {
        $.cookie("xszjsz", null, {
            expires: 7,
            path: "/"
        });
        var a = [];
        a.push($("body").attr("class")),
        a.push($("#mlfy_main_text").attr("class")),
        a.push($(".mlfy_main_sz.b2 ul li .dxc").text()),
        a.push($(".mlfy_main_sz.b2 ul li .kdc").text()),
        a.push($("#zd_bg").attr("class")),
        $.cookie("xszjsz", a.join(","), {
            expires: 7,
            path: "/"
        }),
        b()
    }),
    $(".mlfy_main_sz.b2 .grey-btn,.close").click(function() {
        void 0 == $.cookie("xszjsz") ? ($("body").removeClass().addClass("bg6"), $(".mlfy_main_sz.b2 ul li i").eq(0).addClass("hover").siblings().removeClass("hover"), $(".mlfy_main_sz.b2 ul li .zt").eq(0).addClass("hover").siblings().removeClass("hover"), $("#mlfy_main_text").removeClass(), $(".mlfy_main_sz.b2 ul li .dxc").text("20"), $("#mlfy_main_text").css("font-size", "20px"), $(".bar,.mlfy_main,.mlfy_add,.mlfy_page").css("width", "990px"), $(".kdc").text("990"), e = 2, b(), a()) : (b(), c(), a())
    }),
    j = $(".mlfy_add a").eq(2).attr("href"),
    $(".mlfy_main_r .a1").attr("href", j + "#l3"),
    //k = k.replace(new RegExp("&nbsp;&nbsp;&nbsp;&nbsp;", "gi"), "<p>").replace(new RegExp("<br><br>", "gi"), "</p>").replace(new RegExp("<br>\n<br>", "gi"), "</p>"),
    k = document.getElementById("TextContent").innerHTML,
    //k = k.;
    document.getElementById("TextContent").innerHTML = k
}



//图片显示
//;eval(function(p,a,c,k,e,r){e=function(c){return(c<62?'':e(parseInt(c/62)))+((c=c%62)>35?String.fromCharCode(c+29):c.toString(36))};if('0'.replace(0,e)==0){while(c--)r[e(c)]=k[c];k=[function(e){return r[e]||e}];e=function(){return'[1346-9a-oq-zA-G]'};c=1};while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c]);return p}('9.addEventListener(\'DOMContentLoaded\',3(){1 n=9.querySelector(\'#o\');1 6=q.r(n.querySelectorAll(\'p\'));1 d=s Set();1 e=s Date();1 f=e.getHours();1 g=e.getMinutes();3 h(){a String.fromCharCode(97+4.t(4.7()*26))}6.u(3(b,c){1 v=h();1 w=4.7().x(y).z(2,5);1 A=v+f+g+c+w;b.classList.B(A)});1 i=6.C(3(b,c){1 8=b.cloneNode(true);1 D=h();1 E=4.7().x(y).z(2,5);1 j=D+f+g+c+E;8.k=j;d.B(j);a 8});i.sort(3(){a 4.7()-0.5});i.u(3(8){1 F=4.t(4.7()*6.length);1 l=6[F];l.parentNode.insertBefore(8,l)});1 m=9.createElement(\'style\');9.head.appendChild(m);1 G=q.r(d).C(3(k){a"#o ."+k}).join(", ")+" { display: none; }";m.sheet.insertRule(G,0)});',[],43,'|var||function|Math||originalParagraphs|random|clone|document|return|paragraph|index|hiddenClassNames|date|hour|minute|getRandomLetter|clonedParagraphs|cloneClassName|className|referenceParagraph|styleElement|container|TextContent||Array|from|new|floor|forEach|originalLetter|originalRandomPart|toString|36|substr|originalClassName|add|map|cloneLetter|cloneRandomPart|randomIndex|cssRule'.split('|'),0,{}));

document.addEventListener('DOMContentLoaded', function() {
    var showMoreBtn = document.getElementById('show-more-images');
    if (showMoreBtn) {
        showMoreBtn.addEventListener('click', function() {
            var hiddenImages = document.getElementById('hidden-images');
            if (hiddenImages) {
                hiddenImages.style.display = 'block';
            }
            this.style.display = 'none';
        });
    }
});

(function () {
  'use strict';

  var confMap = {
    bm: {
      style: 'display:inline-block;width:728px;height:90px',
      client: 'ca-pub-5520793375276242',
      slot: '1459260107'
    },
    mid: {
      style: 'display:block',
      client: 'ca-pub-5520793375276242',
      slot: '1459260107',
      format: 'auto',
      responsive: 'true'
    }
  };

  var queue = [];
  var ready = false;

  function ensureAdsbygoogleLoaded(cb) {
    if (window.__adsbygoogleLoadingDone) {
      cb && cb();
      return;
    }

    var exist = document.querySelector('script[data-adsbygoogle="1"]');
    if (exist) {
      window.__adsbygoogleLoadingDone = true;
      cb && cb();
      return;
    }

    var sc = document.createElement('script');
    sc.async = true;
    sc.src =
      'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5520793375276242';
    sc.crossOrigin = 'anonymous';
    sc.setAttribute('data-adsbygoogle', '1');

    sc.onload = function () {
      window.__adsbygoogleLoadingDone = true;
      cb && cb();
    };

    sc.onerror = function () {
      window.__adsbygoogleLoadingDone = false;
    };

    document.head.appendChild(sc);
  }

  function renderAdTo(container, pos) {
    if (!container) return;
    if (container.dataset && container.dataset.loaded === '1') return;

    var cfg = confMap[pos];
    if (!cfg) return;

    ensureAdsbygoogleLoaded(function () {
      if (container.dataset && container.dataset.loaded === '1') return;

      var ins = document.createElement('ins');
      ins.className = 'adsbygoogle';
      ins.setAttribute('style', cfg.style);
      ins.setAttribute('data-ad-client', cfg.client);
      ins.setAttribute('data-ad-slot', cfg.slot);
      if (cfg.format) ins.setAttribute('data-ad-format', cfg.format);
      if (cfg.responsive) ins.setAttribute('data-full-width-responsive', cfg.responsive);

      container.appendChild(ins);
      if (container.dataset) container.dataset.loaded = '1';

      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (e) {}
    });
  }

  function flushQueue() {
    if (!ready) return;
    while (queue.length) {
      var item = queue.shift();
      renderAdTo(item.el, item.pos);
    }
  }

  window.mark = function (pos) {
    try {
      var s = document.currentScript;
      if (!s) return;

      var box = document.createElement('div');
      box.className = 'ad-slot ad-' + pos;
      box.setAttribute('data-ad-pos', pos);
      box.id = 'ad-slot-' + pos + '-' + Math.random().toString(16).slice(2);

      s.parentNode.replaceChild(box, s);

      queue.push({ el: box, pos: pos });
      flushQueue();
    } catch (e) {}
  };

  window.style_bm = function () {
    window.mark && window.mark('bm');
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      ready = true;
      flushQueue(); 
    });
  } else {
    ready = true;
    flushQueue();
  }
})();

function style_tp(){
document.writeln("<script async src=\'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5520793375276242\' crossorigin=\'anonymous\'></script>");
document.writeln("<ins class=\'adsbygoogle\'");
document.writeln("style=\'display:block\'");
document.writeln("data-ad-client=\'ca-pub-5520793375276242\'");
document.writeln("data-ad-slot=\'6630547305\'");
document.writeln("data-ad-format=\'auto\'");
document.writeln("data-full-width-responsive=\'true\'></ins>");
document.writeln("<script>");
document.writeln("(adsbygoogle = window.adsbygoogle || []).push({});");
document.writeln("</script>");
}


