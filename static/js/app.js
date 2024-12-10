document.addEventListener("DOMContentLoaded", () => {
    const deleteButtons = document.querySelectorAll(".delete-button");
    
    deleteButtons.forEach(button => {
        button.addEventListener("click", async (e) => {
            const id = e.target.dataset.id;
            const response = await fetch(`/delete_employee/${id}`, { method: "DELETE" });

            if (response.ok) {
                e.target.closest("tr").remove();
            } else {
                alert("Error deleting employee.");
            }
        });
    });
});
