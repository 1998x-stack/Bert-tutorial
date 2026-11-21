(function () {
  "use strict";
  var STORAGE_KEY = "bert-tutorial-progress-v2";
  function readCompleted() {
    try {
      var parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
      return new Set(Array.isArray(parsed) ? parsed : []);
    } catch (error) {
      return new Set();
    }
  }
  function writeCompleted(completed) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(completed)));
      return true;
    } catch (error) {
      return false;
    }
  }
  function initCatalog() {
    var grid = document.getElementById("chapter-grid");
    if (!grid) return;
    var fallbackNode = document.getElementById("offline-courses");
    var fallback;
    try {
      fallback = JSON.parse(fallbackNode.textContent);
    } catch (error) {
      grid.textContent = "课程目录数据无法解析。";
      return;
    }
    var search = document.getElementById("chapter-search");
    var stageFilter = document.getElementById("stage-filter");
    var reset = document.getElementById("reset-filters");
    var count = document.getElementById("result-count");
    var progressCount = document.getElementById("progress-count");
    var progressFill = document.getElementById("progress-fill");
    var progressNote = document.getElementById("progress-note");
    var completed = readCompleted();
    var dataPromise = location.protocol === "file:"
      ? Promise.resolve(fallback)
      : fetch("courses.json").then(function (response) {
          if (!response.ok) throw new Error("HTTP " + response.status);
          return response.json();
        }).catch(function () { return fallback; });

    dataPromise.then(function (data) {
      var chapters = Array.isArray(data.chapters) ? data.chapters : [];
      function updateProgress() {
        var done = chapters.filter(function (chapter) { return completed.has(chapter.num); }).length;
        var percent = chapters.length ? Math.round(done / chapters.length * 100) : 0;
        progressCount.textContent = done + " / " + chapters.length + " 章已完成";
        progressFill.style.width = percent + "%";
        var progressTrack = document.querySelector(".progress-track");
        if (progressTrack) progressTrack.setAttribute("aria-valuenow", String(percent));
        progressNote.textContent = percent + "% · 进度保存在当前浏览器";
      }
      function render() {
        var term = (search.value || "").trim().toLocaleLowerCase();
        var stage = stageFilter.value;
        var visible = chapters.filter(function (chapter) {
          var haystack = [chapter.num, chapter.title, chapter.summary, chapter.stage].concat(chapter.topics || []).join(" ").toLocaleLowerCase();
          return (!term || haystack.indexOf(term) !== -1) && (!stage || chapter.stageId === stage);
        });
        grid.replaceChildren();
        visible.forEach(function (chapter) {
          var card = document.createElement("article");
          card.className = "chapter-card" + (completed.has(chapter.num) ? " is-complete" : "");
          var top = document.createElement("div");
          top.className = "chapter-card-top";
          var number = document.createElement("span");
          number.className = "chapter-number";
          number.textContent = "CHAPTER " + chapter.num;
          var stageName = document.createElement("span");
          stageName.className = "chapter-stage";
          stageName.textContent = chapter.stage || "课程章节";
          top.append(number, stageName);
          var link = document.createElement("a");
          link.className = "chapter-link";
          link.href = chapter.file;
          link.textContent = chapter.title;
          var summary = document.createElement("p");
          summary.className = "chapter-summary";
          summary.textContent = chapter.summary || (chapter.topics || []).join(" · ");
          var tags = document.createElement("div");
          tags.className = "chapter-tags";
          (chapter.topics || []).slice(0, 3).forEach(function (topic) {
            var tag = document.createElement("span");
            tag.className = "chapter-tag";
            tag.textContent = topic;
            tags.appendChild(tag);
          });
          var bottom = document.createElement("div");
          bottom.className = "chapter-card-bottom";
          var meta = document.createElement("span");
          meta.className = "chapter-meta";
          meta.textContent = (chapter.level || "进阶") + " · " + (chapter.duration || 35) + " 分钟";
          var toggle = document.createElement("button");
          toggle.type = "button";
          toggle.className = "completion-toggle";
          toggle.setAttribute("aria-pressed", String(completed.has(chapter.num)));
          toggle.textContent = completed.has(chapter.num) ? "已完成 ✓" : "标记完成";
          toggle.addEventListener("click", function () {
            if (completed.has(chapter.num)) completed.delete(chapter.num);
            else completed.add(chapter.num);
            writeCompleted(completed);
            render();
            updateProgress();
          });
          bottom.append(meta, toggle);
          card.append(top, link, summary, tags, bottom);
          grid.appendChild(card);
        });
        count.textContent = "显示 " + visible.length + " / " + chapters.length + " 章";
        if (!visible.length) {
          var empty = document.createElement("p");
          empty.className = "empty-state";
          empty.textContent = "没有找到匹配的章节。试试其他关键词或重置筛选条件。";
          grid.appendChild(empty);
        }
      }
      search.addEventListener("input", render);
      stageFilter.addEventListener("change", render);
      reset.addEventListener("click", function () {
        search.value = "";
        stageFilter.value = "";
        render();
      });
      render();
      updateProgress();
    }).catch(function () {
      grid.textContent = "课程目录加载失败。请检查 courses.json 或重新打开页面。";
    });
  }
  function initArticle() {
    var article = document.querySelector(".article-main");
    if (!article) return;
    var progress = document.querySelector(".article-progress span");
    var updateProgress = function () {
      if (!progress) return;
      var scrollable = document.documentElement.scrollHeight - window.innerHeight;
      var amount = scrollable > 0 ? Math.min(100, Math.max(0, window.scrollY / scrollable * 100)) : 0;
      progress.style.width = amount + "%";
    };
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);
    updateProgress();

    var chapterId = document.body.getAttribute("data-chapter-id");
    var completeButton = document.querySelector("[data-mark-complete]");
    if (completeButton && chapterId) {
      var completed = readCompleted();
      function syncButton() {
        var done = completed.has(chapterId);
        completeButton.setAttribute("aria-pressed", String(done));
        completeButton.textContent = done ? "已完成 ✓" : "标记本篇已完成";
      }
      completeButton.addEventListener("click", function () {
        if (completed.has(chapterId)) completed.delete(chapterId);
        else completed.add(chapterId);
        writeCompleted(completed);
        syncButton();
      });
      syncButton();
    }

    document.querySelectorAll("[data-demo]").forEach(function (demo) {
      var statesNode = demo.querySelector("[data-demo-states]");
      var output = demo.querySelector("[data-demo-output]");
      if (!statesNode || !output) return;
      var states;
      try { states = JSON.parse(statesNode.textContent); } catch (error) { return; }
      var buttons = Array.prototype.slice.call(demo.querySelectorAll("[data-demo-action]"));
      buttons.forEach(function (button) {
        button.addEventListener("click", function () {
          var key = button.getAttribute("data-demo-action");
          if (!Object.prototype.hasOwnProperty.call(states, key)) return;
          output.textContent = states[key];
          buttons.forEach(function (other) {
            other.setAttribute("aria-pressed", String(other === button));
          });
        });
      });
    });

    var tokenInput = document.querySelector("[data-wordpiece-input]");
    var tokenButton = document.querySelector("[data-wordpiece-run]");
    var tokenOutput = document.querySelector("[data-wordpiece-output]");
    if (tokenInput && tokenButton && tokenOutput) {
      var toyVocab = new Set(["un", "##believable", "play", "##ing", "##ful", "##er", "believe", "##able", "book", "##s"]);
      function tokenizeToyWord(word) {
        var source = word.toLowerCase();
        if (!source || source.length > 40) return ["[UNK]"];
        var pieces = [];
        var start = 0;
        while (start < source.length) {
          var end = source.length;
          var found = null;
          while (end > start) {
            var piece = (start === 0 ? "" : "##") + source.slice(start, end);
            if (toyVocab.has(piece)) { found = piece; break; }
            end -= 1;
          }
          if (!found) return ["[UNK]"];
          pieces.push(found);
          start = end;
        }
        return pieces;
      }
      tokenButton.addEventListener("click", function () {
        var word = tokenInput.value.trim().replace(/[^a-zA-Z]/g, "");
        var pieces = tokenizeToyWord(word);
        tokenOutput.textContent = word
          ? "输入：" + word + "\n切分：" + pieces.join("  |  ") + "\n说明：这是一个教学玩具词表，不是 bert-base-uncased 的真实 tokenizer 输出。"
          : "请输入一个英文单词。";
      });
    }
  }
  document.addEventListener("DOMContentLoaded", function () {
    initCatalog();
    initArticle();
  });
})();