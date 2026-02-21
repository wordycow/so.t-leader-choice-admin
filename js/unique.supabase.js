(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  U.supabase = {
    db: null,
    init() {
      if (this.db) return this.db;
      this.db = supabase.createClient(U.CONFIG.SUPABASE_URL, U.CONFIG.SUPABASE_KEY);
      return this.db;
    }
  };
})();
