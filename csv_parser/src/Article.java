import java.util.ArrayList;

/**
 * Created by Wang.Daoping on 04.05.2017.
 */
public class Article {

    private String articleID;
    private ArrayList<Feature> features;

    public Article(String articleID){
        this.articleID = articleID;
        this.features = new ArrayList<>();
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
        return features.size();
    }
}
