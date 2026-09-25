using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using RentalRoomManagement.Data;
using RentalRoomManagement.Models;

namespace RentalRoomManagement.Controllers
{
    public class RoomsController : Controller
    {
        private readonly ApplicationDbContext _context;

        public RoomsController(ApplicationDbContext context)
        {
            _context = context;
        }

        // ==========================================
        // HIỂN THỊ DANH SÁCH PHÒNG
        // ==========================================
        public async Task<IActionResult> Index()
        {
            var rooms = await _context.Rooms.ToListAsync();

            return View(rooms);
        }

        // ==========================================
        // HIỂN THỊ FORM THÊM PHÒNG
        // ==========================================
        [HttpGet]
        public IActionResult Create()
        {
            return View();
        }

        // ==========================================
        // XỬ LÝ THÊM PHÒNG
        // ==========================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Create(Room room)
        {
            if (!ModelState.IsValid)
            {
                return View(room);
            }

            // Phòng mới mặc định là phòng trống
            room.Status = "Trống";

            _context.Rooms.Add(room);

            await _context.SaveChangesAsync();

            TempData["Success"] = "Thêm phòng thành công.";

            return RedirectToAction(nameof(Index));
        }

        // ==========================================
        // XÓA PHÒNG
        // ==========================================
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<IActionResult> Delete(int id)
        {
            var room = await _context.Rooms.FindAsync(id);

            // Không tìm thấy phòng
            if (room == null)
            {
                TempData["Error"] = "Không tìm thấy phòng cần xóa.";

                return RedirectToAction(nameof(Index));
            }

            // Không cho xóa phòng đang thuê
            if (room.Status == "Đang thuê")
            {
                TempData["Error"] = "Không thể xóa phòng đang được thuê.";

                return RedirectToAction(nameof(Index));
            }

            // Xóa phòng
            _context.Rooms.Remove(room);

            await _context.SaveChangesAsync();

            TempData["Success"] = "Xóa phòng thành công.";

            return RedirectToAction(nameof(Index));
        }
    }
}