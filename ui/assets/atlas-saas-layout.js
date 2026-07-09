(function () {
  const page = document.body.dataset.atlasPage;
  if (!page || document.body.dataset.atlasShellReady === "true") return;
  document.body.dataset.atlasShellReady = "true";

  const titles = {
    dashboard: {
      eyebrow: "The Lion's Den",
      title: "Good Morning Manny",
      subtitle: "Kingdom Builder • Massive Action. Maximum Effort. Minimal Money."
    },
    missions: {
      eyebrow: "Atlas Mission Control",
      title: "Executive operations dashboard",
      subtitle: "Assign work, monitor active missions, and review runtime updates without leaving the live Atlas Operating System flow."
    },
    crm: {
      eyebrow: "Atlas CRM",
      title: "Customer Command",
      subtitle: "Revenue-first relationship tracking for SIS, FRESH, and RAMFAM Kingdom."
    },
    gallery: {
      eyebrow: "Atlas Design Gallery",
      title: "Design Gallery",
      subtitle: "Review real Kingdom Gallery assets, approvals, publication status, and revenue signals."
    },
    commerce: {
      eyebrow: "Atlas Commerce",
      title: "Commerce Center",
      subtitle: "Review the latest commerce approval dashboard without leaving the signed-in Atlas app shell."
    }
  };

  const navSections = [
    {
      title: "The Pride",
      items: [
        { key: "missions", href: "/missions", label: "Mission Control" },
        { key: "crm", href: "/crm", label: "Customer Command" },
        { key: "commerce", href: "/commerce-command-center", label: "Commerce Center" },
        { key: "gallery", href: "/design-gallery", label: "Design Gallery" },
        { key: "knowledge", href: "/ramfam", label: "Knowledge Base" }
      ]
    },
    {
      title: "Finance",
      items: [
        { key: "revenue", href: "/app#finance", label: "Revenue" },
        { key: "expenses", href: "/app#finance", label: "Expenses" },
        { key: "paypal", href: "/app#finance", label: "PayPal" },
        { key: "invoices", href: "/app#finance", label: "Invoices" }
      ]
    },
    {
      title: "Marketing",
      items: [
        { key: "campaigns", href: "/neural#atlas-chat", label: "Campaigns" },
        { key: "social", href: "/neural#atlas-chat", label: "Social Media" },
        { key: "website", href: "/sis/", label: "Website" }
      ]
    },
    {
      title: "System",
      items: [
        { key: "settings", href: "/login", label: "Settings" },
        { key: "logout", href: "/logout", label: "Logout" }
      ]
    }
  ];

  function navLink(item) {
    return `<a class="atlas-saas-nav-link" href="${item.href}" ${item.key === page ? 'aria-current="page"' : ""}>${item.label}</a>`;
  }

  const navMarkup = navSections.map(section => `
    <div class="atlas-saas-nav-title">${section.title}</div>
    ${section.items.map(navLink).join("")}
  `).join("");

  const existing = Array.from(document.body.childNodes);
  const shell = document.createElement("div");
  shell.className = "atlas-saas-shell";

  const sidebar = document.createElement("aside");
  sidebar.className = "atlas-saas-sidebar";
  sidebar.setAttribute("aria-label", "Atlas signed-in navigation");
  sidebar.innerHTML = `
    <div class="atlas-saas-brand">
      <div class="atlas-saas-brand-mark">🦁</div>
      <div><h1>THE LION'S DEN</h1><p>Executive Dashboard</p></div>
    </div>
    <a class="atlas-saas-nav-link" href="/app" ${page === "dashboard" ? 'aria-current="page"' : ""}>Executive Dashboard</a>
    ${navMarkup}
    <div class="atlas-saas-note">Executive Headquarters: Mission Control, CRM, Commerce, Gallery, finance readiness, and live executive feed in one signed-in shell.</div>
  `;

  const main = document.createElement("main");
  main.className = "atlas-saas-main";
  const config = titles[page] || titles.dashboard;
  if (document.body.dataset.atlasCustomTopbar === "true") {
    main.innerHTML = "";
  } else {
    main.innerHTML = `
      <header class="atlas-saas-topbar">
        <div>
          <p class="atlas-saas-eyebrow">${config.eyebrow}</p>
          <h2 class="atlas-saas-title">${config.title}</h2>
          <p class="atlas-saas-subtitle">${config.subtitle}</p>
        </div>
        <div class="atlas-saas-live-pill"><span class="atlas-saas-pulse"></span><span>Live data routes</span></div>
      </header>
    `;
  }

  const content = document.createElement("div");
  content.className = "atlas-content-wrap";
  existing.forEach(node => content.appendChild(node));
  main.appendChild(content);
  shell.append(sidebar, main);
  document.body.appendChild(shell);
})();
