import javafx.application.Application;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.stage.Screen;
import javafx.geometry.Rectangle2D;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.paint.Color;
import javafx.scene.shape.ArcType;
import javafx.stage.Stage;
import javafx.scene.shape.*;
import javafx.scene.text.Text;
import javafx.animation.Timeline;
import javafx.animation.KeyFrame;
import javafx.animation.PauseTransition;
import javafx.event.*;
import javafx.util.Duration;
import javafx.animation.TranslateTransition;
import javafx.scene.input.KeyCode;
import javafx.scene.control.Label;
import javafx.scene.text.Font;
import javafx.scene.control.TextField;
public class Grid
{
	private TextField flag_area;
	private Circle[] circles;
	private int[] visited_circles;
	private Group group;
	static float RADIUS = 10.0f;
	private int linecount = 0;
	private Line currentline;
	private Line[] lines;
	private Scene scene;
	private double margin = 60;
	private double header = 40;
	private double footer = 80;
	private Label label;
	private Label title;
	private float font_size = 30.0f;
	private long res = 0;
	private byte[] key;
	boolean disable_click = false;
	boolean disable_dragging = false;
	private Scene lockscreen;
	private Scene winscreen;
	public Grid(Stage stg, float x0, float y0, int nw, int nh) // spacing between tiles is x0/y0, number of items on each side is nw/nh
	{
		this.circles = new Circle[nw*nh];
		this.lines = new Line[nw*nh-1];
		this.visited_circles = new int[9];
		for (int k = 0; k < 9; k++) this.visited_circles[k] = -1;
		this.group = new Group();
		for (int i = 0; i < nh; i++)
			for (int j = 0; j < nw; j++)
			{
				//System.out.println(i + " * " + nw + " + " + j + " = " + (i*nw+j));
				circles[i*nw+j] = new Circle();
				circles[i*nw+j].setCenterX(margin+(double)j*x0);
				circles[i*nw+j].setCenterY(header+margin+(double)i*y0); 
				circles[i*nw+j].setRadius(RADIUS);
				this.group.getChildren().add(circles[i*nw+j]);
			}
		this.flag_area = new TextField("L.O.C.K.E.D");
		this.flag_area.setLayoutX(15);
		this.flag_area.setLayoutY(320);
		this.flag_area.setPrefColumnCount(24);
		this.flag_area.setOnKeyPressed(event -> {
			event.consume();
		});
		this.flag_area.setOnKeyTyped(event -> {
			event.consume();
		});
		//this.flag_area.setDisable(true);
		this.group.getChildren().add(flag_area);
		/*this.title = new Label("Crackme 2.0");
		this.title.setLayoutX((2*margin+x0*(nw-1))/2-4*this.font_size/2);
		this.title.setLayoutY(header/2-font_size/2);
		this.title.setFont(new Font(font_size));
		this.group.getChildren().add(this.title);
		*/
		/*this.label = new Label();
		this.label.setLayoutX((2*margin+x0*(nw-1))/2-4*this.font_size/2);
		this.label.setLayoutY(header+margin+y0*(nh-1)+footer/2);
		this.label.setFont(new Font(font_size));
		this.group.getChildren().add(this.label);
		*/
		this.lockscreen = new Scene(this.group, x0 * (nw-1) + 2*margin, y0 * (nh-1) + 2*margin + header + footer, Color.WHITE);
		this.lockscreen.setOnMousePressed(event -> {
			/*if (this.linecount == 0 &&
				(Math.abs(event.getSceneX() - margin) > RADIUS ||
				 Math.abs(event.getSceneY() - margin) > RADIUS)
			) return;*/
			if (disable_click) return;
			boolean found = false;
			for (int i = 0; i < nh && !found; i++)
				for (int j = 0; j < nw && !found; j++)
					if (Math.abs(event.getSceneX() - circles[i*nw+j].getCenterX()) < RADIUS &&
						Math.abs(event.getSceneY() - circles[i*nw+j].getCenterY()) < RADIUS
					)
					{
						this.currentline = new Line();
						this.currentline.setStartX(circles[i*nw+j].getCenterX());
						this.currentline.setStartY(circles[i*nw+j].getCenterY());
						this.currentline.setEndX(circles[i*nw+j].getCenterX());
						this.currentline.setEndY(circles[i*nw+j].getCenterY());
						this.currentline.setStrokeWidth(2.0);
						this.group.getChildren().add(this.currentline);
						this.visited_circles[i*nw+j] = 0;
						disable_click = true;
						disable_dragging = false;
					}
		});
		this.lockscreen.setOnMouseDragged(event -> {
			if (disable_dragging) return;
			if (this.currentline != null)
			{
				double x2 = event.getSceneX();
				double y2 = event.getSceneY();
				double x1 = this.currentline.getStartX();
				double y1 = this.currentline.getStartY();
				this.currentline.setEndX(x2);
				this.currentline.setEndY(y2);
				for (int i = 0; i < nh; i++)
					for (int j = 0; j < nw; j++)
					{
						if (this.visited_circles[i*nw+j] != -1) continue;
						double x3 = this.circles[i*nw+j].getCenterX(), y3 = this.circles[i*nw+j].getCenterY();
						if (Math.abs(x3 - x2) < RADIUS && Math.abs(y3 - y2) < RADIUS)
						{
							this.currentline.setEndX(circles[i*nw+j].getCenterX());
							this.currentline.setEndY(circles[i*nw+j].getCenterY());
							this.lines[this.linecount] = this.currentline;

							//if (this.linecount == 0) this.visited_circles[i*nw + j] = this.linecount;
							//this.x = j;
							//this.y = i;
							this.visited_circles[i*nw + j] = ++this.linecount;
							if (this.linecount == 8)
							{
								disable_dragging = true;
								break;
							}
							this.currentline = new Line();
							this.currentline.setStartX(circles[i*nw+j].getCenterX());
							this.currentline.setStartY(circles[i*nw+j].getCenterY());
							this.currentline.setEndX(x2);
							this.currentline.setEndY(y2);
							this.currentline.setStrokeWidth(2.0);
							this.group.getChildren().add(this.currentline);
							break;
						}
					}
			}
		});
		this.lockscreen.setOnMouseReleased(event -> {
			if (disable_dragging == false) this.group.getChildren().remove(this.currentline);
			if (this.linecount < 3) 
			{
				this.clear();
				this.disable_dragging = true;
				this.disable_click = false;
				return;
			}
			byte[] k = VerificationUtils.check(this.visited_circles);
			if (k != null)
			{
				for (int i = 0; i < this.lines.length; i++)
					this.lines[i].setStroke(Color.GREEN);
				this.key = k;
				this.flag_area.setText("Decrypting the flag, please wait");
				setTimeout(this::win, 4);
			}
			else
			{
				for (int i = 0; i < this.linecount; i++)
					this.lines[i].setStroke(Color.RED);
				setTimeout(this::clear, 2);
			}
			this.disable_dragging = true;
			this.disable_click = false;
		});
		stg.setScene(this.lockscreen);
		stg.show();
	}
	private void win()
	{
		this.flag_area.setText(VerificationUtils.decrypt_flag(key));
	}
	private void clear()
	{
		for (int i = 0; i < 9; i++)
			this.visited_circles[i] = -1;
		for (int i = 0; i < this.linecount; i++)
		{
			this.group.getChildren().remove(this.lines[i]);
			this.lines[i] = null;
		}
		this.linecount = 0;
	}
	private static void setTimeout(Runnable r, int delay)
	{
		PauseTransition pt = new PauseTransition(Duration.seconds(delay));
		pt.setOnFinished( event -> r.run() );
		pt.play();
	}
	public Scene getScene()
	{
		return this.scene;
	}
	
	public Group getGroup()
	{
		return this.group;
	}
}
