import turtle
import random


def draw_branch(t, branch_length, angle, width):
    if branch_length < 10:  # Base case: stop recursion when branches get too small
        t.color('green')  # Leaf color
        t.begin_fill()
        t.circle(3)
        t.end_fill()
        return

    # Draw the main branch
    t.pensize(width)
    t.forward(branch_length)

    # Save the current position and heading
    saved_x, saved_y = t.position()
    saved_heading = t.heading()

    # Right sub-branch
    t.right(angle)
    # Generate slightly different length and width for natural look
    new_length = branch_length * random.uniform(0.7, 0.8)
    new_width = width * 0.8
    draw_branch(t, new_length, angle, new_width)

    # Restore position to branch point
    t.penup()
    t.goto(saved_x, saved_y)
    t.setheading(saved_heading)
    t.pendown()

    # Left sub-branch
    t.left(angle)
    new_length = branch_length * random.uniform(0.6, 0.8)
    draw_branch(t, new_length, angle, new_width)


def main():
    screen = turtle.Screen()
    screen.bgcolor('turquoise')

    t = turtle.Turtle()
    t.speed(-3)  # Fastest speed
    t.penup()
    t.goto(0, -200)  # Start from bottom of screen
    t.pendown()
    t.left(90)  # Point upward
    t.color('brown')

    draw_branch(t, 150, 30, 20)

    screen.exitonclick()


if __name__ == "__main__":
    main()