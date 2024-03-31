document.addEventListener("DOMContentLoaded", () => {
  const emailForm = document.getElementById("emailForm");
  emailForm.addEventListener("submit", sendEmail);

  function sendEmail(event) {
    event.preventDefault();
    const name = document.getElementById("name").value;
    const from = document.getElementById("from").value;
    const subject = document.getElementById("subject").value;
    const message = document.getElementById("message").value;

    // Send email using EmailJS and the following are my account secret keys
    emailjs.send("service_ctsw0vk", "template_jipxice", {
      name: name,
      from: from,
      subject: subject,
      message: message
    }, "_1Pi1XEw7MSM4PvJG")
    .then(function(response) {
      console.log("Email sent successfully:", response);
      alert("Email sent successfully!");

      // Clearing form fields after click the send message button
      document.getElementById("name").value = "";
      document.getElementById("from").value = "";
      document.getElementById("subject").value = "";
      document.getElementById("message").value = "";
    }, function(error) {
      console.error("Error sending email:", error);
      alert("Error sending email. Please try again.");
    });
  }
});
