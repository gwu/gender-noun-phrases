import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.stream.Collectors;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.trees.Constituent;
import edu.stanford.nlp.trees.LabeledScoredConstituentFactory;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeCoreAnnotations;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class EnglishParserTest {
  @Test
  void parsesTestSentenceIntoSyntaxTree() {
    // set up pipeline properties
    final Properties props = new Properties();
    props.setProperty("annotators", "tokenize,ssplit,pos,parse");
    // use faster shift reduce parser
    props.setProperty("parse.model", "edu/stanford/nlp/models/srparser/englishSR.ser.gz");
    props.setProperty("parse.maxlen", "100");

    // set up Stanford CoreNLP pipeline
    final StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
    // build annotation for a review
    final Annotation annotation =
        new Annotation("The small red car turned very quickly around the corner.");
    // annotate
    pipeline.annotate(annotation);
    // get tree
    final Tree tree = annotation
        .get(CoreAnnotations.SentencesAnnotation.class)
        .get(0)
        .get(TreeCoreAnnotations.TreeAnnotation.class);

    final Set<Constituent> treeConstituents =
        tree.constituents(new LabeledScoredConstituentFactory());
    for (Constituent constituent : treeConstituents) {
      if (constituent.label() != null && constituent.label().toString().equals("NP")) {
        List<Tree> words =
            tree.getLeaves().subList(constituent.start(), constituent.end() + 1);
        final String phrase = String.join(
            " ", words.stream().map(Object::toString).collect(Collectors.toList()));
        System.out.println(phrase);
      }
    }
  }
}
