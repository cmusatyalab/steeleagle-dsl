package org.droneDSL.compile.preprocess.Visualizer;

import org.droneDSL.compile.Compiler;
import org.droneDSL.compile.preprocess.partition.Partition;
import org.droneDSL.compile.preprocess.partition.SurveyPartition;
import org.droneDSL.compile.preprocess.waypoints.GeoPoints;
import org.droneDSL.compile.preprocess.waypoints.WaypointsUtils;
import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Envelope;
import org.locationtech.jts.geom.Polygon;

import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseEvent;
import java.awt.event.MouseMotionListener;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Path2D;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class Visualizer extends JPanel implements MouseMotionListener {

  private final List<Polygon> polygons;
  private final List<List<Coordinate>> allCoordinates;
  private final Envelope globalBounds;

  private static final int PADDING = 50;
  private static final int PANEL_SIZE = 600;
  private static final int POINT_SIZE = 6;
  private static final int HOVER_RADIUS = 8;

  private double scaleX, scaleY;
  private int panelWidth, panelHeight;
  private double offsetX, offsetY;

  public Visualizer(List<Polygon> polygons, List<List<Coordinate>> allCoordinates) {
    this.polygons = polygons;
    this.allCoordinates = allCoordinates;
    this.globalBounds = computeGlobalEnvelope(polygons);
    setPreferredSize(new Dimension(PANEL_SIZE, PANEL_SIZE));
    addMouseMotionListener(this);
    setToolTipText("");
  }

  private Envelope computeGlobalEnvelope(List<Polygon> polygons) {
    Envelope env = new Envelope();
    for (Polygon p : polygons) {
      env.expandToInclude(p.getEnvelopeInternal());
    }
    return env;
  }

  @Override
  protected void paintComponent(Graphics g) {
    super.paintComponent(g);
    panelWidth = getWidth();
    panelHeight = getHeight();

    double width = Math.max(globalBounds.getWidth(), 1e-6);
    double height = Math.max(globalBounds.getHeight(), 1e-6);

    scaleX = (panelWidth - 2.0 * PADDING) / width;
    scaleY = (panelHeight - 2.0 * PADDING) / height;

    double uniformScale = Math.min(scaleX, scaleY);
    scaleX = scaleY = uniformScale;

    offsetX = globalBounds.getMinX();
    offsetY = globalBounds.getMinY();

    Graphics2D g2 = (Graphics2D) g;
    g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

    g2.translate(PADDING, panelHeight - PADDING);
    g2.scale(1, -1);
    g2.translate(-offsetX * scaleX, -offsetY * scaleY);

    drawAll(g2);
  }

  private void drawAll(Graphics2D g2) {
    g2.setStroke(new BasicStroke(1.5f));

    // Draw polygons
    for (Polygon p : polygons) {
      g2.setColor(Color.BLUE);
      Path2D path = new Path2D.Double();
      Coordinate[] coords = p.getCoordinates();
      path.moveTo(coords[0].x * scaleX, coords[0].y * scaleY);
      for (int i = 1; i < coords.length; i++) {
        path.lineTo(coords[i].x * scaleX, coords[i].y * scaleY);
      }
      path.closePath();
      g2.draw(path);
    }

    // Draw waypoint paths and points
    for (List<Coordinate> coords : allCoordinates) {
      if (coords.size() >= 2) {
        g2.setColor(Color.ORANGE);
        Path2D path = new Path2D.Double();
        path.moveTo(coords.get(0).x * scaleX, coords.get(0).y * scaleY);
        for (int i = 1; i < coords.size(); i++) {
          path.lineTo(coords.get(i).x * scaleX, coords.get(i).y * scaleY);
        }
        g2.draw(path);
      }

      // Draw points
      g2.setColor(Color.RED);
      for (Coordinate c : coords) {
        double x = c.x * scaleX;
        double y = c.y * scaleY;
        g2.fill(new Ellipse2D.Double(x - POINT_SIZE / 2.0, y - POINT_SIZE / 2.0, POINT_SIZE, POINT_SIZE));
      }
    }
  }

  @Override
  public void mouseMoved(MouseEvent e) {
    int mouseX = e.getX() - PADDING;
    int mouseY = panelHeight - e.getY() - PADDING;

    for (List<Coordinate> coordList : allCoordinates) {
      for (Coordinate coord : coordList) {
        double screenX = (coord.x - offsetX) * scaleX;
        double screenY = (coord.y - offsetY) * scaleY;
        double dist = Math.hypot(screenX - mouseX, screenY - mouseY);
        if (dist <= HOVER_RADIUS) {
          setToolTipText(String.format("(%.6f, %.6f)", coord.x, coord.y));
          return;
        }
      }
    }
    setToolTipText(null);
  }

  @Override
  public void mouseDragged(MouseEvent e) {}

  public static void main(String[] args) {
    String kmlPath = "./example/fieldB.kml";
    double spacing = 5;
    double angle = 0;
    double trigger = 10;

    Partition partition = new SurveyPartition(spacing, angle, trigger); // Use SurveyPartition

    Map<String, GeoPoints> rawGeoPointsMap = WaypointsUtils.parseKMLFile(kmlPath);
    Map<String, List<GeoPoints>> partitionedMap = Compiler.getPartitionedGeoPointsMap(partition, rawGeoPointsMap);

    List<Polygon> polygons = new ArrayList<>();
    List<List<Coordinate>> allWaypoints = new ArrayList<>();

    for (String area : rawGeoPointsMap.keySet()) {
      GeoPoints rawGeo = rawGeoPointsMap.get(area);
      List<GeoPoints> waypointsList = partitionedMap.get(area);

      polygons.add(rawGeo.toPolygon());

      // assuming GeoPoints has getCoordinates()
      allWaypoints.addAll(waypointsList);
    }

    JFrame frame = new JFrame("Partition Visualizer - All Areas");
    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    frame.add(new Visualizer(polygons, allWaypoints));
    frame.pack();
    frame.setLocationRelativeTo(null);
    frame.setVisible(true);
  }
}
