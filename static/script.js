$(document).ready(function () {
  $("#refresh-btn").click(function () {
    $("#refresh-btn")
      .prop("disabled", true)
      .html(`<i class="fas fa-spinner fa-spin"></i> Refreshing...`);

    fetch("/api/refresh", {
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          location.reload(); // Reloads data by refreshing the page
        } else {
          alert("Failed to refresh data.");
        }
      })
      .catch((err) => {
        console.error("Refresh error:", err);
        alert("An error occurred while refreshing.");
      })
      .finally(() => {
        $("#refresh-btn")
          .prop("disabled", false)
          .html(`<i class="fas fa-sync-alt"></i> Refresh Dining Data`);
      });
  });

  $("#ask-ai-btn").click(function () {
    submitQuery();
  });

  $("#ai-query").keypress(function (event) {
    if (event.which === 13) {
      // Check if enter key is pressed
      event.preventDefault();
      submitQuery();
    }
  });

  function submitQuery() {
    let query = $("#ai-query").val().trim();

    if (query === "") {
      $("#ai-response")
        .html(
          `<p class="text-danger"><i class="fas fa-exclamation-circle"></i> Please enter a question.</p>`
        )
        .removeClass("d-none");
      return;
    }

    // Show loading state
    $("#ai-response")
      .html(`<p><i class="fas fa-spinner fa-spin"></i> Thinking...</p>`)
      .removeClass("d-none");

    // Send query to the API
    fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          $("#ai-response").html(
            `<p class="text-warning"><i class="fas fa-exclamation-triangle"></i> ${data.error}</p>`
          );
        } else {
          $("#ai-response").html(
            `<p><i class="fas fa-lightbulb"></i> ${data.response}</p>`
          );
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        $("#ai-response").html(
          `<p class="text-danger"><i class="fas fa-times-circle"></i> Failed to get response.</p>`
        );
      });
  }

  let selectedStatuses = new Set();
  let selectedCategories = new Set();

  // Fetch dining hall data
  fetch("/api/dining-halls")
    .then((response) => response.json())
    .then((data) => {
      $("#dining-container").html(""); // Clear loading text
      if (data.length === 0) {
        $("#dining-container").append(
          "<p class='text-center'>No dining halls available.</p>"
        );
        return;
      }
      data.forEach((hall) => {
        $("#dining-container").append(`
          <div class="col dining-hall" data-status="${
            hall.status
          }" data-category="${hall.type}">
              <div class="card dining-card shadow-sm p-3 rounded d-flex flex-column mx-auto" 
                  data-name="${hall.name}" 
                  data-status="${hall.status}" 
                  data-hours="${hall.hours}" 
                  data-type="${hall.type}" 
                  data-menu="${hall.menu_url}"
                  style="cursor: pointer; transition: transform 0.2s ease-in-out;">
                  
                  <!-- Card Header -->
                  <div class="d-flex align-items-center justify-content-between">
                    <h5 class="fw-bold mb-1">${hall.name}</h5>
                    <span class="badge ${getBadgeColor(hall.status)}">${
          hall.status
        }</span>
                  </div>
      
                  <!-- Card Body -->
                  <div class="mt-2">
                    ${
                      hall.status !== "Closed"
                        ? `<p class="text-muted mb-0"><strong>Hours:</strong> ${hall.hours}</p>`
                        : ""
                    }
                  </div>
      
                  <!-- Card Footer -->
                <div class="d-flex align-items-center justify-content-between mt-3">
                  <a href="${
                    hall.menu_url
                  }" target="_blank" class="btn btn-outline-dark btn-sm">Visit Website</a>
                  <div class="d-flex align-items-center">
                    <div class="card-icon fs-3 text-muted me-2">${getFontAwesomeIcon(
                      hall.type
                    )}</div>
                    <i class="fas fa-chevron-right text-muted chevron-icon"></i> 
                  </div>
                </div>
              </div>
          </div>
      `);
      });

      // Open modal on card click
      $(".dining-card").click(function () {
        let name = $(this).data("name");
        let status = $(this).data("status");
        let hours = $(this).data("hours");
        let type = $(this).data("type");
        let menuUrl = $(this).data("menu");

        $("#modal-dining-name").text(name);
        $("#modal-status").text(status);
        $("#modal-type").text(type);

        if (status === "Closed") {
          // if (false) {
          $("#modal-hours").hide();
          $("#modal-menu").hide();
          $("#modal-menu-link").hide();
          $("#modal-body-content").html(
            `<p class="text-center text-danger"><i class="fa-solid fa-ban"></i> This location is currently closed.</p>`
          );
        } else {
          $("#modal-hours").show().text(`Hours: ${hours}`);
          $("#modal-menu").show();
          $("#modal-menu-link").show();
          $("#modal-menu-link").attr("href", menuUrl);

          // Fetch menu data for this dining hall
          fetch(`/api/menu?name=${encodeURIComponent(name)}`)
            .then((response) => response.json())
            .then((menuData) => {
              if (menuData.error) {
                $("#modal-body-content").html(
                  `<p class="text-center text-warning"><i class="fa-solid fa-triangle-exclamation"></i> No menu data available.</p>`
                );
              } else {
                let menuHtml = `
  <p class="fw-bold mb-2">Currently Serving <span>(${menuData.meal_time})</span>:</p>
  <ul class="ps-3">`;

                menuData.menu_items.forEach((station) => {
                  menuHtml += `
    <li class="mb-2">
      <span class="fw-semibold">${station.station}:</span>
      <ul class="ps-3 mt-1">`;

                  station.items.forEach((item) => {
                    let prefs = item.preferences
                      ? `&nbsp;&nbsp;<span class="fst-italic p-1 d-inline-flex align-items-center" style="color: #003366; background-color: #e6f0ff; border-radius: 5px; font-size: 0.8rem; line-height: 1;">${item.preferences}</span>`
                      : "";
                    let allergens = item.allergens
                      ? `<div class="text-muted small mb-1 ${
                          item.preferences ? "mt-1" : ""
                        }" style="font-size: 0.85rem;">${item.allergens}</div>`
                      : "";

                    menuHtml += `
        <li>
          <span style="font-weight: 500;">${item.name}</span>${prefs}
          ${allergens}
        </li>`;
                  });

                  menuHtml += `
      </ul>
    </li>`;
                });

                menuHtml += `</ul>`;
                $("#modal-body-content").html(menuHtml);
              }
            })
            .catch((error) => {
              console.error("Error fetching menu:", error);
              $("#modal-body-content").html(
                `<p class="text-center text-danger"><i class="fa-solid fa-xmark"></i> Failed to load menu.</p>`
              );
            });
        }

        $("#diningModal").modal("show");
      });

      // Apply filters initially
      applyFilters();
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
      $("#dining-container").html(
        "<p class='text-center text-danger'>Failed to load data.</p>"
      );
    });

  $(".filter-btn").click(function () {
    let status = $(this).data("filter");
    toggleSelection(selectedStatuses, status, $(this));
    applyFilters();
  });

  $(".category-btn").click(function () {
    let category = $(this).data("category");
    toggleSelection(selectedCategories, category, $(this));
    applyFilters();
  });

  function toggleSelection(set, value, button) {
    if (set.has(value)) {
      set.delete(value);
      button.removeClass("active");
    } else {
      set.add(value);
      button.addClass("active");
    }
  }

  function applyFilters() {
    $(".dining-hall").each(function () {
      let status = $(this).data("status");
      let category = $(this).data("category");

      let statusMatch =
        selectedStatuses.size === 0 || selectedStatuses.has(status);
      let categoryMatch =
        selectedCategories.size === 0 || selectedCategories.has(category);

      if (statusMatch && categoryMatch) {
        $(this).show();
      } else {
        $(this).hide();
      }
    });
  }

  function getBadgeColor(status) {
    if (status === "Open") return "bg-success";
    if (status === "Closing Soon") return "bg-warning";
    if (status === "Closed") return "bg-danger";
    return "secondary";
  }

  // Function to add icons based on dining type
  function getFontAwesomeIcon(type) {
    if (type.includes("Dining Hall")) return `<i class="fas fa-utensils"></i>`;
    if (type.includes("Retail Café")) return `<i class="fas fa-coffee"></i>`;
    return `<i class="fas fa-store"></i>`;
  }

  function autoTriggerRefresh() {
    const now = new Date();
    const minute = now.getMinutes();

    if (minute === 1 || minute === 31) {
      console.log("Auto-refresh triggered at", now.toLocaleTimeString());

      fetch("/api/refresh", {
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.message) {
            location.reload(); // Refresh page after success
          } else {
            console.warn("Auto-refresh failed to return success message.");
          }
        })
        .catch((err) => {
          console.error("Auto-refresh error:", err);
        });
    }
  }

  // Check every minute
  setInterval(autoTriggerRefresh, 60000);
});
