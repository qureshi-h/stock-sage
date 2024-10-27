exports.paginate = (page = 1, size = 20) => {
    const limit = parseInt(size);
    const offset = (parseInt(page) - 1) * limit;
    return { limit, offset };
  };
  