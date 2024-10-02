document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Ball properties
        let ballRadius = 10;
        let x = canvas.width / 2;
        let y = canvas.height - 30;
        let ballSpeed = 200; // pixels per second
        let angle = -Math.PI / 4; // Initial angle (upwards)
        let dx = ballSpeed * Math.cos(angle);
        let dy = ballSpeed * Math.sin(angle);

        // Paddle properties
        const paddleHeight = 10;
        const paddleWidth = 75;
        let paddleX = (canvas.width - paddleWidth) / 2;
        const paddleSpeed = 300; // pixels per second

        // Brick properties
        const brickRowCount = 3;
        const brickColumnCount = 5;
        const brickWidth = 75;
        const brickHeight = 20;
        const brickPadding = 10;
        const brickOffsetTop = 30;
        const brickOffsetLeft = 30;

        // Create bricks
        const bricks = [];
        let remainingBricks = 0;
        for (let c = 0; c < brickColumnCount; c++) {
            bricks[c] = [];
            for (let r = 0; r < brickRowCount; r++) {
                bricks[c][r] = { x: 0, y: 0, status: 1 };
                remainingBricks++;
            }
        }

        // Keyboard controls
        let rightPressed = false;
        let leftPressed = false;
        let isPaused = false;

        let lastTime = 0;

        document.addEventListener("keydown", keyDownHandler);
        document.addEventListener("keyup", keyUpHandler);

        function keyDownHandler(e) {
            if (e.key === "Right" || e.key === "ArrowRight") {
                rightPressed = true;
            } else if (e.key === "Left" || e.key === "ArrowLeft") {
                leftPressed = true;
            } else if (e.key === " ") {
                togglePause();
            }
        }

        function keyUpHandler(e) {
            if (e.key === "Right" || e.key === "ArrowRight") {
                rightPressed = false;
            } else if (e.key === "Left" || e.key === "ArrowLeft") {
                leftPressed = false;
            }
        }

        function togglePause() {
            isPaused = !isPaused;
            if (!isPaused) {
                lastTime = performance.now();
                requestAnimationFrame(draw);
            }
        }

        function drawBall() {
            ctx.beginPath();
            ctx.arc(x, y, ballRadius, 0, Math.PI * 2);
            ctx.fillStyle = "#0095DD";
            ctx.fill();
            ctx.closePath();
        }

        function drawPaddle() {
            ctx.beginPath();
            ctx.rect(paddleX, canvas.height - paddleHeight, paddleWidth, paddleHeight);
            ctx.fillStyle = "#0095DD";
            ctx.fill();
            ctx.closePath();
        }

        function drawBricks() {
            for (let c = 0; c < brickColumnCount; c++) {
                for (let r = 0; r < brickRowCount; r++) {
                    if (bricks[c][r].status === 1) {
                        const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
                        const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
                        bricks[c][r].x = brickX;
                        bricks[c][r].y = brickY;
                        ctx.beginPath();
                        ctx.rect(brickX, brickY, brickWidth, brickHeight);
                        ctx.fillStyle = "#0095DD";
                        ctx.fill();
                        ctx.closePath();
                    }
                }
            }
        }

        function drawBrickCount() {
            ctx.font = "16px Arial";
            ctx.fillStyle = "#0095DD";
            ctx.fillText("Bricks remaining: " + remainingBricks, 8, 20);
        }

        function collisionDetection(newX, newY) {
            let collided = false;
            for (let c = 0; c < brickColumnCount; c++) {
                for (let r = 0; r < brickRowCount; r++) {
                    const b = bricks[c][r];
                    if (b.status === 1) {
                        if (newX > b.x - ballRadius && newX < b.x + brickWidth + ballRadius &&
                            newY > b.y - ballRadius && newY < b.y + brickHeight + ballRadius) {

                            // Determine which side of the brick was hit
                            const overlapLeft = newX - (b.x - ballRadius);
                            const overlapRight = (b.x + brickWidth + ballRadius) - newX;
                            const overlapTop = newY - (b.y - ballRadius);
                            const overlapBottom = (b.y + brickHeight + ballRadius) - newY;

                            // Find the smallest overlap
                            const minOverlap = Math.min(overlapLeft, overlapRight, overlapTop, overlapBottom);

                            if (minOverlap === overlapLeft || minOverlap === overlapRight) {
                                dx = -dx;
                            } else {
                                dy = -dy;
                            }

                            b.status = 0;
                            remainingBricks--;
                            collided = true;
                            break;
                        }
                    }
                }
                if (collided) break;
            }
            return collided;
        }

        function drawPauseScreen() {
            ctx.font = "30px Arial";
            ctx.fillStyle = "#0095DD";
            ctx.textAlign = "center";
            ctx.fillText("PAUSED", canvas.width / 2, canvas.height / 2);
        }

        function draw(currentTime) {
            if (lastTime === 0) {
                lastTime = currentTime;
            }
            const deltaTime = (currentTime - lastTime) / 1000; // Convert to seconds
            lastTime = currentTime;

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawBricks();
            drawBall();
            drawPaddle();
//            drawBrickCount();

            if (!isPaused) {
                // Update ball position
                let newX = x + dx * deltaTime;
                let newY = y + dy * deltaTime;

                // Ball collision with walls
                if (newX - ballRadius < 0 || newX + ballRadius > canvas.width) {
                    dx = -dx;
                    newX = x; // Revert to previous position
                }
                if (newY - ballRadius < 0) {
                    dy = -dy;
                    newY = ballRadius; // Set to top of screen
                } else if (newY + ballRadius > canvas.height - paddleHeight) {
                    if (newX > paddleX && newX < paddleX + paddleWidth) {
                        dy = -dy;
                        newY = canvas.height - paddleHeight - ballRadius; // Set to top of paddle
                    } else {
                        alert("GAME OVER");
                        document.location.reload();
                        return;
                    }
                }

                // Check for brick collisions
                if (!collisionDetection(newX, newY)) {
                    x = newX;
                    y = newY;
                }

                // Update paddle position
                if (rightPressed && paddleX < canvas.width - paddleWidth) {
                    paddleX = Math.min(paddleX + paddleSpeed * deltaTime, canvas.width - paddleWidth);
                } else if (leftPressed && paddleX > 0) {
                    paddleX = Math.max(paddleX - paddleSpeed * deltaTime, 0);
                }

                // Check for win condition
                if (remainingBricks === 0) {
                    alert("Congratulations! You've won!");
                    document.location.reload();
                    return;
                }
            } else {
                drawPauseScreen();
            }

            requestAnimationFrame(draw);
        }

        requestAnimationFrame(draw);
});