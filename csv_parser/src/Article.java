import java.util.ArrayList;

/**
 * Created by Wang.Daoping on 04.05.2017.
 */
public class Article {

    private String articleID;
    private ArrayList<Feature> features;
    private ArrayList<Float> price;
    private float avgPrice;
    private String brand;

    public Article(String articleID){
        this.articleID = articleID;
        this.features = new ArrayList<>();
        this.price = new ArrayList<>();
        this.brand = "unknown";
    }

    public String getBrand(){
        return brand;
    }

    public void setBrand(String brand){
        this.brand = brand;
    }

    public void addFeature(String featureName, String featureValue){
        for(int i = 0; i < this.features.size(); i++){
            if(this.features.get(i).getName().equals(featureName)){
                //System.out.println("Duplicated feature value detected: " + this.articleID + "\t" + this.features.get(i).getName() + "\told: " + this.features.get(i).getValue() + "\tnew:" + featureValue);
                return;
            }
        }
        Feature feature = new Feature(featureName, featureValue);
        this.features.add(feature);
    }

    public void addFeature(String featureName){
        for(int i = 0; i < this.features.size(); i++){
            if(this.features.get(i).getName().equals(featureName)){
                System.out.println("Duplicated feature value detected: " + this.articleID + "\t" + this.features.get(i).getName());
                return;
            }
        }
        Feature feature = new Feature(featureName);
        this.features.add(feature);
    }

    public ArrayList<Feature> getFeatures(){
        return features;
    }

    public String getArticleID(){
        return this.articleID;
    }

    public int getNumFeatures(){
        return this.features.size();
    }

    public ArrayList<Float> getPrice(){ return this.price; }

    public void addPrice(float price) {
        this.price.add(price);
    }

    public float getAvgPrice(){
        return this.avgPrice;
    }

    public void calculateAvgPrice(){
        this.avgPrice = 0;
        for(int i = 0; i < this.price.size(); i++){
            avgPrice += this.price.get(i);
        }
        avgPrice = avgPrice / this.price.size();
    }

    @Override public boolean equals(Object o){
        if(o instanceof Article)
            return ((Article) o).getArticleID().equals(this.getArticleID());
        else if(o instanceof String)
            return o.equals(this.getArticleID());
        return false;
    }
}
