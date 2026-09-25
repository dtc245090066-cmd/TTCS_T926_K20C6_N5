using Microsoft.EntityFrameworkCore;
using RentalRoomManagement.Data;

var builder = WebApplication.CreateBuilder(args);

// ========================================
// 1. Đăng ký MVC
// ========================================
builder.Services.AddControllersWithViews();

// ========================================
// 2. Kết nối Entity Framework Core với SQL Server
// ========================================
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(
        builder.Configuration.GetConnectionString("DefaultConnection")
    )
);

var app = builder.Build();

// ========================================
// 3. Cấu hình môi trường
// ========================================
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

// ========================================
// 4. Middleware
// ========================================
app.UseHttpsRedirection();

app.UseStaticFiles();

app.UseRouting();

app.UseAuthorization();

// ========================================
// 5. Cấu hình Route mặc định
// ========================================
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}"
);

// ========================================
// 6. Chạy ứng dụng
// ========================================
app.Run();