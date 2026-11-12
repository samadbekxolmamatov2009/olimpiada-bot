(function () {
  const tg = window.Telegram ? window.Telegram.WebApp : null;
  if (tg) {
    tg.ready();
    tg.expand();
    tg.enableClosingConfirmation();
  }

  const initData = tg ? tg.initData : "";

  const els = {
    loading: document.getElementById("loading"),
    closed: document.getElementById("closed"),
    registered: document.getElementById("registered"),
    success: document.getElementById("success"),
    successText: document.getElementById("successText"),
    form: document.getElementById("form"),
    adminNote: document.getElementById("adminNote"),
    fullName: document.getElementById("fullName"),
    district: document.getElementById("district"),
    school: document.getElementById("school"),
    parentPhone: document.getElementById("parentPhone"),
    formError: document.getElementById("formError"),
    submitBtn: document.getElementById("submitBtn"),
    closeBtn: document.getElementById("closeBtn"),
  };

  let selectedGrade = null;
  let isAdmin = false;

  const ERROR_MESSAGES = {
    already_registered: "Siz allaqachon ro'yxatdan o'tgansiz.",
    closed: "Ro'yxatdan o'tish muddati tugagan.",
    invalid_grade: "Faqat 3- va 4-sinf o'quvchilari qatnashishi mumkin.",
    invalid_fields: "Iltimos, barcha maydonlarni to'g'ri to'ldiring.",
    invalid_init_data: "Ma'lumot tasdiqlanmadi. Botni qayta ishga tushiring.",
  };

  function show(id) {
    ["loading", "closed", "registered", "success", "form"].forEach((key) => {
      els[key].classList.toggle("hidden", key !== id);
    });
  }

  function validate() {
    const ok =
      els.fullName.value.trim().length >= 3 &&
      els.district.value.trim().length > 0 &&
      els.school.value.trim().length > 0 &&
      selectedGrade !== null &&
      els.parentPhone.value.replace(/\D/g, "").length >= 9;
    els.submitBtn.disabled = !ok;
    return ok;
  }

  document.querySelectorAll(".grade-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".grade-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      selectedGrade = parseInt(btn.dataset.grade, 10);
      validate();
    });
  });

  [els.fullName, els.district, els.school, els.parentPhone].forEach((input) => {
    input.addEventListener("input", validate);
  });

  function resetForm() {
    els.form.reset();
    document.querySelectorAll(".grade-btn").forEach((b) => b.classList.remove("active"));
    selectedGrade = null;
    validate();
  }

  async function loadStatus() {
    try {
      const res = await fetch("/api/status?init_data=" + encodeURIComponent(initData));
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "error");

      if (data.role === "admin") {
        isAdmin = true;
        els.adminNote.classList.remove("hidden");
        show("form");
      } else if (data.role === "registered") {
        show("registered");
      } else if (data.role === "closed") {
        show("closed");
      } else {
        show("form");
      }
    } catch (e) {
      els.formError.textContent = ERROR_MESSAGES[e.message] || "Ulanishda xatolik yuz berdi. Qayta urinib ko'ring.";
      els.formError.classList.remove("hidden");
      show("form");
    }
  }

  els.form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!validate()) return;

    els.submitBtn.disabled = true;
    els.submitBtn.textContent = "Yuborilmoqda...";
    els.formError.classList.add("hidden");

    try {
      const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          init_data: initData,
          full_name: els.fullName.value.trim(),
          district: els.district.value.trim(),
          school: els.school.value.trim(),
          grade: selectedGrade,
          parent_phone: els.parentPhone.value.trim(),
        }),
      });
      const data = await res.json();

      if (!res.ok) {
        throw new Error(ERROR_MESSAGES[data.error] || "Xatolik yuz berdi. Qayta urinib ko'ring.");
      }

      if (tg && tg.HapticFeedback) tg.HapticFeedback.notificationOccurred("success");

      if (isAdmin) {
        els.successText.textContent = "O'quvchi ro'yxatga muvaffaqiyatli qo'shildi.";
        show("success");
        setTimeout(() => {
          resetForm();
          show("form");
        }, 1600);
      } else {
        els.successText.textContent = "Navoiy–Qorako'l olimpiadasi bo'yicha ma'lumotlaringiz qabul qilindi.";
        show("success");
      }
    } catch (err) {
      els.formError.textContent = err.message;
      els.formError.classList.remove("hidden");
      show("form");
    } finally {
      els.submitBtn.textContent = "✅ Ro'yxatdan o'tish";
      validate();
    }
  });

  if (els.closeBtn) {
    els.closeBtn.addEventListener("click", () => {
      if (tg) tg.close();
    });
  }

  show("loading");
  loadStatus();
})();
