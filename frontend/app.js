/* =========================
   CONFIGURATION
========================= */

const API_URL = window.location.origin;


/* =========================
   HELPERS
========================= */

function formatCurrency(amount) {

    const value =
        Number(amount) || 0;

    return new Intl.NumberFormat(
        "en-NG",
        {
            style: "currency",
            currency: "NGN",
            minimumFractionDigits: 2
        }
    ).format(value);
}


function formatDate(dateString) {

    if (!dateString) {
        return "-";
    }

    const date =
        new Date(dateString + "T00:00:00");

    if (Number.isNaN(date.getTime())) {
        return dateString;
    }

    return date.toLocaleDateString(
        "en-NG",
        {
            day: "numeric",
            month: "short",
            year: "numeric"
        }
    );
}


async function apiRequest(
    url,
    options = {}
) {

    const response =
        await fetch(url, {
            ...options,

            headers: {
                "Content-Type":
                    "application/json",

                "Accept":
                    "application/json",

                ...(options.headers || {})
            }
        });

    if (!response.ok) {

        let message =
            `Request failed (${response.status})`;

        try {

            const data =
                await response.json();

            if (data.detail) {

                message =
                    typeof data.detail === "string"
                        ? data.detail
                        : JSON.stringify(
                            data.detail
                        );

            }

        } catch (_) {
            // Use default error.
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}


/* =========================
   NAVIGATION
========================= */

const sectionNames = {
    dashboard: {
        title: "Dashboard",
        subtitle:
            "Here's what's happening with your money."
    },

    transactions: {
        title: "Transactions",
        subtitle:
            "Manage all your income and expenses."
    },

    budgets: {
        title: "Budgets",
        subtitle:
            "Set spending limits for your categories."
    },

    reports: {
        title: "Reports",
        subtitle:
            "Review your financial activity."
    }
};


function showSection(sectionName) {

    document
        .querySelectorAll(".page-section")
        .forEach(section => {

            section.classList.remove("active");

        });


    const section =
        document.getElementById(
            `${sectionName}Section`
        );


    if (section) {
        section.classList.add("active");
    }


    document
        .querySelectorAll(".nav-item")
        .forEach(button => {

            button.classList.toggle(
                "active",
                button.dataset.section ===
                sectionName
            );

        });


    const page =
        sectionNames[sectionName];


    if (page) {

        document.getElementById(
            "pageTitle"
        ).textContent =
            page.title;

        document.getElementById(
            "pageSubtitle"
        ).textContent =
            page.subtitle;
    }


    if (sectionName === "dashboard") {
        loadDashboard();
    }

    if (sectionName === "transactions") {
        loadTransactions();
    }

    if (sectionName === "budgets") {
        loadBudgets();
    }

}


document
    .querySelectorAll(".nav-item")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                showSection(
                    button.dataset.section
                );

            }
        );

    });


document
    .getElementById(
        "viewTransactionsBtn"
    )
    .addEventListener(
        "click",
        () => {

            showSection(
                "transactions"
            );

        }
    );


/* =========================
   DASHBOARD SUMMARY
========================= */

async function loadSummary() {

    try {

        const data =
            await apiRequest(
                `${API_URL}/summary/`
            );


        document.getElementById(
            "balance"
        ).textContent =
            formatCurrency(
                data.balance
            );


        document.getElementById(
            "income"
        ).textContent =
            formatCurrency(
                data.total_income
            );


        document.getElementById(
            "expenses"
        ).textContent =
            formatCurrency(
                data.total_expenses
            );

    } catch (error) {

        console.error(
            "Summary error:",
            error
        );

    }

}


/* =========================
   CATEGORY SUMMARY
========================= */

async function loadCategories() {

    const container =
        document.getElementById(
            "categories"
        );


    try {

        const data =
            await apiRequest(
                `${API_URL}/summary/categories`
            );


        container.innerHTML = "";


        const entries =
            Object.entries(data || {});


        if (!entries.length) {

            container.innerHTML =
                `<div class="empty-state">
                    No spending data yet.
                </div>`;

            return;
        }


        entries
            .sort(
                (a, b) =>
                    Number(b[1]) -
                    Number(a[1])
            )
            .forEach(
                ([category, amount]) => {

                    const row =
                        document.createElement(
                            "div"
                        );

                    row.className =
                        "category-row";

                    row.innerHTML = `
                        <span class="category-name">
                            ${escapeHtml(category)}
                        </span>

                        <span class="category-amount">
                            ${formatCurrency(amount)}
                        </span>
                    `;

                    container.appendChild(row);

                }
            );


    } catch (error) {

        console.error(
            "Category error:",
            error
        );

        container.innerHTML =
            `<div class="empty-state">
                Unable to load categories.
            </div>`;

    }

}


/* =========================
   DASHBOARD TRANSACTIONS
========================= */

async function loadRecentTransactions() {

    const container =
        document.getElementById(
            "recentTransactions"
        );


    try {

        const data =
            await apiRequest(
                `${API_URL}/transactions/`
            );


        container.innerHTML = "";


        if (!Array.isArray(data) || !data.length) {

            container.innerHTML =
                `<div class="empty-state">
                    No transactions yet.
                </div>`;

            return;
        }


        const recent =
            [...data]
                .sort(
                    (a, b) =>
                        Number(b.id || 0) -
                        Number(a.id || 0)
                )
                .slice(0, 5);


        recent.forEach(
            transaction => {

                const row =
                    document.createElement(
                        "div"
                    );

                row.className =
                    "transaction-row";


                const type =
                    transaction.transaction_type;


                const amountClass =
                    type === "income"
                        ? "amount-income"
                        : "amount-expense";


                const sign =
                    type === "income"
                        ? "+"
                        : "-";


                row.innerHTML = `
                    <div class="transaction-main">

                        <strong>
                            ${escapeHtml(
                                transaction.category
                            )}
                        </strong>

                        <span>
                            ${escapeHtml(
                                transaction.description ||
                                "No description"
                            )}
                        </span>

                    </div>

                    <div
                        class="transaction-amount ${amountClass}"
                    >
                        ${sign}
                        ${formatCurrency(
                            transaction.amount
                        )}
                    </div>
                `;


                container.appendChild(row);

            }
        );


    } catch (error) {

        console.error(
            "Recent transactions error:",
            error
        );

        container.innerHTML =
            `<div class="empty-state">
                Unable to load transactions.
            </div>`;

    }

}


/* =========================
   TRANSACTION TABLE
========================= */

async function loadTransactions() {

    const tableBody =
        document.getElementById(
            "transactionsTableBody"
        );

    const empty =
        document.getElementById(
            "transactionsEmpty"
        );


    try {

        const data =
            await apiRequest(
                `${API_URL}/transactions/`
            );


        tableBody.innerHTML = "";


        if (!Array.isArray(data) || !data.length) {

            empty.classList.remove(
                "hidden"
            );

            return;
        }


        empty.classList.add(
            "hidden"
        );


        [...data]
            .sort(
                (a, b) =>
                    Number(b.id || 0) -
                    Number(a.id || 0)
            )
            .forEach(
                transaction => {

                    const row =
                        document.createElement(
                            "tr"
                        );


                    const isIncome =
                        transaction.transaction_type ===
                        "income";


                    const badgeClass =
                        isIncome
                            ? "badge-income"
                            : "badge-expense";


                    const amountClass =
                        isIncome
                            ? "amount-income"
                            : "amount-expense";


                    const sign =
                        isIncome
                            ? "+"
                            : "-";


                    row.innerHTML = `
                        <td>
                            ${formatDate(
                                transaction.transaction_date
                            )}
                        </td>

                        <td>
                            <strong>
                                ${escapeHtml(
                                    transaction.category
                                )}
                            </strong>
                        </td>

                        <td>
                            ${escapeHtml(
                                transaction.description ||
                                "-"
                            )}
                        </td>

                        <td>
                            <span
                                class="badge ${badgeClass}"
                            >
                                ${escapeHtml(
                                    transaction.transaction_type
                                )}
                            </span>
                        </td>

                        <td>
                            <strong
                                class="${amountClass}"
                            >
                                ${sign}
                                ${formatCurrency(
                                    transaction.amount
                                )}
                            </strong>
                        </td>

                        <td>

                            <div class="table-actions">

                                <button
                                    class="small-btn edit-btn"
                                    type="button"
                                    onclick="editTransaction(${transaction.id})"
                                >
                                    Edit
                                </button>

                                <button
                                    class="small-btn delete-btn"
                                    type="button"
                                    onclick="deleteTransaction(${transaction.id})"
                                >
                                    Delete
                                </button>

                            </div>

                        </td>
                    `;


                    tableBody.appendChild(row);

                }
            );


    } catch (error) {

        console.error(
            "Transactions error:",
            error
        );

        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    Unable to load transactions.
                </td>
            </tr>
        `;

    }

}


/* =========================
   TRANSACTION MODAL
========================= */

const transactionModal =
    document.getElementById(
        "transactionModal"
    );

const transactionForm =
    document.getElementById(
        "transactionForm"
    );


function openTransactionModal(
    transaction = null
) {

    const title =
        document.getElementById(
            "transactionModalTitle"
        );

    const formError =
        document.getElementById(
            "formError"
        );


    if (!transactionModal) {

        console.error(
            "Transaction modal not found."
        );

        return;
    }


    if (!transactionForm) {

        console.error(
            "Transaction form not found."
        );

        return;
    }


    formError.textContent = "";


    if (transaction) {

        title.textContent =
            "Edit Transaction";


        document.getElementById(
            "amount"
        ).value =
            transaction.amount ?? "";


        document.getElementById(
            "transactionType"
        ).value =
            transaction.transaction_type ??
            "expense";


        document.getElementById(
            "category"
        ).value =
            transaction.category ?? "";


        document.getElementById(
            "description"
        ).value =
            transaction.description ?? "";


        document.getElementById(
            "transactionDate"
        ).value =
            transaction.transaction_date ?? "";


        transactionForm.dataset.editingId =
            transaction.id;

    } else {

        title.textContent =
            "Add Transaction";


        transactionForm.reset();


        transactionForm.dataset.editingId =
            "";


        document.getElementById(
            "transactionType"
        ).value =
            "expense";


        document.getElementById(
            "transactionDate"
        ).value =
            new Date()
                .toISOString()
                .split("T")[0];

    }


    transactionModal.classList.add(
        "active"
    );


    transactionModal.setAttribute(
        "aria-hidden",
        "false"
    );


    document.body.style.overflow =
        "hidden";


    setTimeout(
        () => {

            document
                .getElementById("amount")
                .focus();

        },
        50
    );

}


function closeTransactionModal() {

    if (!transactionModal) {
        return;
    }


    transactionModal.classList.remove(
        "active"
    );


    transactionModal.setAttribute(
        "aria-hidden",
        "true"
    );


    document.body.style.overflow =
        "";


    transactionForm.reset();


    transactionForm.dataset.editingId =
        "";


    document.getElementById(
        "formError"
    ).textContent = "";

}


/* =========================
   ADD TRANSACTION BUTTONS
========================= */

document
    .getElementById(
        "addTransactionBtn"
    )
    .addEventListener(
        "click",
        event => {

            event.preventDefault();

            openTransactionModal();

        }
    );


document
    .getElementById(
        "transactionsAddBtn"
    )
    .addEventListener(
        "click",
        event => {

            event.preventDefault();

            openTransactionModal();

        }
    );


document
    .getElementById(
        "closeTransactionModal"
    )
    .addEventListener(
        "click",
        closeTransactionModal
    );


document
    .getElementById(
        "cancelTransaction"
    )
    .addEventListener(
        "click",
        closeTransactionModal
    );


transactionModal.addEventListener(
    "click",
    event => {

        if (
            event.target ===
            transactionModal
        ) {
            closeTransactionModal();
        }

    }
);


document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Escape" &&
            transactionModal.classList.contains(
                "active"
            )
        ) {
            closeTransactionModal();
        }

    }
);


/* =========================
   SAVE TRANSACTION
========================= */

transactionForm.addEventListener(
    "submit",
    async event => {

        event.preventDefault();


        const formError =
            document.getElementById(
                "formError"
            );


        formError.textContent = "";


        const amount =
            Number(
                document.getElementById(
                    "amount"
                ).value
            );


        const transactionType =
            document.getElementById(
                "transactionType"
            ).value;


        const category =
            document.getElementById(
                "category"
            ).value.trim();


        const description =
            document.getElementById(
                "description"
            ).value.trim();


        const transactionDate =
            document.getElementById(
                "transactionDate"
            ).value;


        if (!amount || amount <= 0) {

            formError.textContent =
                "Please enter a valid amount.";

            return;
        }


        if (!category) {

            formError.textContent =
                "Please enter a category.";

            return;
        }


        if (!transactionDate) {

            formError.textContent =
                "Please select a date.";

            return;
        }


        const payload = {

            amount,

            transaction_type:
                transactionType,

            category,

            description:
                description || null,

            transaction_date:
                transactionDate

        };


        const editingId =
            transactionForm.dataset.editingId;


        try {

            if (editingId) {

                await apiRequest(
                    `${API_URL}/transactions/${editingId}`,
                    {
                        method: "PUT",

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );

            } else {

                await apiRequest(
                    `${API_URL}/transactions/`,
                    {
                        method: "POST",

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );

            }


            closeTransactionModal();


            await loadDashboard();

            await loadTransactions();


        } catch (error) {

            console.error(
                "Save transaction error:",
                error
            );

            formError.textContent =
                error.message;

        }

    }
);


/* =========================
   EDIT TRANSACTION
========================= */

async function editTransaction(id) {

    try {

        const transaction =
            await apiRequest(
                `${API_URL}/transactions/${id}`
            );


        openTransactionModal(
            transaction
        );


    } catch (error) {

        alert(
            `Unable to load transaction: ${error.message}`
        );

    }

}


/* =========================
   DELETE TRANSACTION
========================= */

async function deleteTransaction(id) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this transaction?"
        );


    if (!confirmed) {
        return;
    }


    try {

        await apiRequest(
            `${API_URL}/transactions/${id}`,
            {
                method: "DELETE"
            }
        );


        await loadDashboard();

        await loadTransactions();


    } catch (error) {

        alert(
            `Unable to delete transaction: ${error.message}`
        );

    }

}


/* =========================
   BUDGETS
========================= */

function setDefaultBudgetDate() {

    const now =
        new Date();


    document.getElementById(
        "budgetMonth"
    ).value =
        now.getMonth() + 1;


    document.getElementById(
        "budgetYear"
    ).value =
        now.getFullYear();

}


async function loadBudgets() {

    const container =
        document.getElementById(
            "budgetList"
        );


    try {

        const data =
            await apiRequest(
                `${API_URL}/budgets/`
            );


        container.innerHTML = "";


        if (
            !Array.isArray(data) ||
            !data.length
        ) {

            container.innerHTML =
                `<div class="empty-state">
                    No budgets yet.
                </div>`;

            return;
        }


        data.forEach(
            budget => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =
                    "budget-item";


                item.innerHTML = `
                    <div class="budget-top">

                        <span class="budget-category">
                            ${escapeHtml(
                                budget.category
                            )}
                        </span>

                        <span class="budget-limit">
                            ${formatCurrency(
                                budget.amount
                            )}
                        </span>

                    </div>

                    <div class="budget-meta">

                        <span>
                            ${getMonthName(
                                budget.month
                            )}
                            ${budget.year}
                        </span>

                        <span>
                            Budget
                        </span>

                    </div>
                `;


                container.appendChild(item);

            }
        );


    } catch (error) {

        console.error(
            "Budgets error:",
            error
        );

        container.innerHTML =
            `<div class="empty-state">
                Unable to load budgets.
            </div>`;

    }

}


/* =========================
   CREATE BUDGET
========================= */

document
    .getElementById(
        "budgetForm"
    )
    .addEventListener(
        "submit",
        async event => {

            event.preventDefault();


            const errorElement =
                document.getElementById(
                    "budgetFormError"
                );


            errorElement.textContent =
                "";


            const category =
                document.getElementById(
                    "budgetCategory"
                ).value.trim();


            const amount =
                Number(
                    document.getElementById(
                        "budgetAmount"
                    ).value
                );


            const month =
                Number(
                    document.getElementById(
                        "budgetMonth"
                    ).value
                );


            const year =
                Number(
                    document.getElementById(
                        "budgetYear"
                    ).value
                );


            if (!category) {

                errorElement.textContent =
                    "Enter a category.";

                return;
            }


            if (!amount || amount <= 0) {

                errorElement.textContent =
                    "Enter a valid budget amount.";

                return;
            }


            if (
                !Number.isInteger(month) ||
                month < 1 ||
                month > 12
            ) {

                errorElement.textContent =
                    "Month must be between 1 and 12.";

                return;
            }


            if (
                !Number.isInteger(year) ||
                year < 2000
            ) {

                errorElement.textContent =
                    "Year must be an integer.";

                return;
            }


            try {

                await apiRequest(
                    `${API_URL}/budgets/`,
                    {
                        method: "POST",

                        body:
                            JSON.stringify({
                                category,
                                amount,
                                month,
                                year
                            })
                    }
                );


                event.target.reset();

                setDefaultBudgetDate();

                await loadBudgets();


            } catch (error) {

                console.error(
                    "Create budget error:",
                    error
                );

                errorElement.textContent =
                    error.message;

            }

        }
    );


document
    .getElementById(
        "refreshBudgetsBtn"
    )
    .addEventListener(
        "click",
        loadBudgets
    );


/* =========================
   REPORTS
========================= */

function setDefaultReportDate() {

    const now =
        new Date();


    document.getElementById(
        "reportYear"
    ).value =
        now.getFullYear();

}


document
    .getElementById(
        "generateReportBtn"
    )
    .addEventListener(
        "click",
        generateReport
    );


async function generateReport() {

    const year =
        Number(
            document.getElementById(
                "reportYear"
            ).value
        );


    const month =
        document.getElementById(
            "reportMonth"
        ).value;


    const result =
        document.getElementById(
            "reportResult"
        );


    if (
        !Number.isInteger(year) ||
        year < 2000
    ) {

        result.innerHTML =
            `<div class="empty-state">
                Please enter a valid year.
            </div>`;

        return;
    }


    try {

        let url =
            `${API_URL}/reports/?year=${year}`;


        if (month) {

            url +=
                `&month=${Number(month)}`;

        }


        const data =
            await apiRequest(url);


        const income =
            Number(
                data.total_income ??
                data.income ??
                0
            );


        const expenses =
            Number(
                data.total_expenses ??
                data.expenses ??
                0
            );


        const balance =
            Number(
                data.balance ??
                income - expenses
            );


        result.innerHTML = `
            <div class="report-summary">

                <div class="report-stat">
                    <span>Total Income</span>

                    <strong
                        class="amount-income"
                    >
                        ${formatCurrency(
                            income
                        )}
                    </strong>
                </div>


                <div class="report-stat">
                    <span>Total Expenses</span>

                    <strong
                        class="amount-expense"
                    >
                        ${formatCurrency(
                            expenses
                        )}
                    </strong>
                </div>


                <div class="report-stat">
                    <span>Balance</span>

                    <strong>
                        ${formatCurrency(
                            balance
                        )}
                    </strong>
                </div>

            </div>
        `;


    } catch (error) {

        console.error(
            "Report error:",
            error
        );


        result.innerHTML =
            `<div class="empty-state">
                Unable to generate report:
                ${escapeHtml(
                    error.message
                )}
            </div>`;

    }

}


/* =========================
   SECURITY HELPER
========================= */

function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/* =========================
   DATE HELPERS
========================= */

function getMonthName(month) {

    const names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ];


    return names[
        Number(month) - 1
    ] || "Unknown";
}


/* =========================
   DASHBOARD LOADER
========================= */

async function loadDashboard() {

    await Promise.all([
        loadSummary(),
        loadCategories(),
        loadRecentTransactions()
    ]);

}


/* =========================
   INITIALIZATION
========================= */

setDefaultBudgetDate();

setDefaultReportDate();

showSection("dashboard");


if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/sw.js")
            .then(registration => {
                console.log(
                    "Service worker registered:",
                    registration.scope
                );
            })
            .catch(error => {
                console.error(
                    "Service worker registration failed:",
                    error
                );
            });
    });
}
