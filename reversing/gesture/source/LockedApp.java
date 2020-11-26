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
import javafx.animation.Timeline;
import javafx.animation.KeyFrame;
import javafx.event.*;
import javafx.util.Duration;
import javafx.animation.TranslateTransition;
import javafx.scene.control.TextField;
public class LockedApp extends Application {
	Rectangle2D screenBounds;
	public static Point[] pts;// = { new Point(20.0f
	public static void main(String[] args)
	{
		launch(args);
	}
	@Override
	public void start(Stage primaryStage) {
		//this.screenBounds = Screen.getPrimary().getVisualBounds();
		Grid grr = new Grid(primaryStage, 90, 90, 3, 3);//(30, 30, 35, 7);
   }
}
