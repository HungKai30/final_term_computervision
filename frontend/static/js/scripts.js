document.addEventListener("DOMContentLoaded", () => {
  console.log("Student Attendance System: JavaScript Loaded.");

  // Example: Handle form submissions
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      // You can add form validation or data handling here
      console.log("Form Submitted:", form.action);
    });
  });
});
