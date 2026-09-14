css = open('frontend/dist/assets/index-DL2tCVup.css', encoding='utf-8').read()

checks = {
    'no @import': '@import' not in css,
    'body bg f0fdf4': '#f0fdf4' in css,
    'root width 100pct important': 'width:100%!important' in css,
    'sidebar fixed': 'position:fixed' in css,
    'lg ml-64': '16rem' in css,
    'nav-item': 'nav-item' in css,
    'agri-card': 'agri-card' in css,
    'btn-primary': 'btn-primary' in css,
    'bubble-user': 'bubble-user' in css,
    'slide-up animation': 'agri-slide-up' in css,
    'spin animation': 'agri-spin' in css,
    'plus jakarta sans': 'Plus Jakarta Sans' in css,
    '100vh': '100vh' in css,
    'no 1126px constraint': '1126' not in css,
}

all_ok = True
for k, v in checks.items():
    status = "OK" if v else "FAIL"
    print(f"  [{status}] {k}")
    if not v:
        all_ok = False

print()
print("RESULT:", "ALL PASS" if all_ok else "FAILURES FOUND")
print("CSS size:", len(css), "bytes")
