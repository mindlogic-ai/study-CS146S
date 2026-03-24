const errorHandler = (err, req, res, _next) => {
    console.error(err.stack);
    if (err.name === "ValidationError") {
        return res.status(400).json({ error: err.message });
    }
    if (err.name === "CastError") {
        return res.status(404).json({ error: "Resource not found" });
    }
    res.status(500).json({ error: "Internal server error" });
};

export default errorHandler;
